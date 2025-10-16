import random
from typing import List, Dict, Optional
from collections import Counter
from django.utils import timezone
from django.db.models import Avg, Count, Q


class RecommendationService:
    """
    Serviço de IA básica para recomendações de times e projetos.
    """
    
    def get_team_allocation_recommendations(self, project) -> List[Dict]:
        """
        Gerar recomendações de alocação de time para um projeto.
        """
        from apps.recommendations.models import Recommendation
        from apps.accounts.models import User
        from apps.skills.models import UserSkill
        
        recommendations = []
        
        # Se o projeto já tem um time, analisar se está bem formado
        if project.team:
            team_analysis = self._analyze_existing_team(project)
            if team_analysis['recommendations']:
                recommendations.extend(team_analysis['recommendations'])
        else:
            # Sugerir formação de time
            team_suggestions = self._suggest_team_formation(project)
            recommendations.extend(team_suggestions)
        
        # Salvar recomendações no banco
        for rec_data in recommendations:
            Recommendation.objects.update_or_create(
                content_object=project,
                type='team_allocation',
                title=rec_data['title'],
                defaults={
                    'description': rec_data['description'],
                    'confidence': rec_data['confidence'],
                    'score': rec_data['score'],
                    'data': rec_data['data']
                }
            )
        
        return recommendations
    
    def get_delay_risk_recommendations(self, project) -> List[Dict]:
        """
        Analisar risco de atraso e gerar recomendações.
        """
        from apps.recommendations.models import Recommendation
        from apps.tasks.models import Task
        
        risk_analysis = self._calculate_delay_risk(project)
        recommendations = []
        
        if risk_analysis['risk_level'] == 'high':
            recommendations.append({
                'title': 'Alto Risco de Atraso Detectado',
                'description': f"""
                O projeto apresenta alto risco de atraso baseado na análise:
                - {risk_analysis['overdue_tasks']} tarefas em atraso
                - Velocity atual: {risk_analysis['velocity']:.1f} pontos/sprint
                - Progresso: {risk_analysis['progress']:.1f}%
                
                Recomendações:
                1. Revisar escopo e prioridades
                2. Adicionar recursos ao time
                3. Implementar daily standups
                """,
                'confidence': 'high',
                'score': risk_analysis['risk_score'],
                'data': risk_analysis
            })
        elif risk_analysis['risk_level'] == 'medium':
            recommendations.append({
                'title': 'Monitorar Progresso do Projeto',
                'description': f"""
                O projeto apresenta alguns sinais de alerta:
                - Progresso atual: {risk_analysis['progress']:.1f}%
                - {risk_analysis['overdue_tasks']} tarefas em atraso
                
                Ações sugeridas:
                1. Revisar prazos das tarefas pendentes
                2. Verificar bloqueios com o time
                """,
                'confidence': 'medium',
                'score': risk_analysis['risk_score'],
                'data': risk_analysis
            })
        
        # Salvar recomendações
        for rec_data in recommendations:
            Recommendation.objects.update_or_create(
                content_object=project,
                type='delay_risk',
                title=rec_data['title'],
                defaults={
                    'description': rec_data['description'],
                    'confidence': rec_data['confidence'],
                    'score': rec_data['score'],
                    'data': rec_data['data']
                }
            )
        
        return recommendations
    
    def get_scrum_role_recommendations(self, project) -> List[Dict]:
        """
        Sugerir papéis Scrum ideais para membros do time.
        """
        from apps.recommendations.models import Recommendation
        
        if not project.team:
            return []
        
        role_suggestions = self._analyze_scrum_roles(project.team)
        recommendations = []
        
        for suggestion in role_suggestions:
            recommendations.append({
                'title': f'Sugestão de Papel: {suggestion["recommended_role"]}',
                'description': f"""
                Recomendamos {suggestion["user"].get_full_name()} para o papel de {suggestion["recommended_role"]}.
                
                Razões:
                {chr(10).join(f"- {reason}" for reason in suggestion["reasons"])}
                
                Score de compatibilidade: {suggestion["score"]:.1f}/100
                """,
                'confidence': suggestion['confidence'],
                'score': suggestion['score'] / 100,
                'data': {
                    'user_id': suggestion['user'].id,
                    'current_role': suggestion['current_role'],
                    'recommended_role': suggestion['recommended_role'],
                    'reasons': suggestion['reasons']
                }
            })
        
        # Salvar recomendações
        for rec_data in recommendations:
            Recommendation.objects.update_or_create(
                content_object=project,
                type='role_suggestion',
                title=rec_data['title'],
                defaults={
                    'description': rec_data['description'],
                    'confidence': rec_data['confidence'],
                    'score': rec_data['score'],
                    'data': rec_data['data']
                }
            )
        
        return recommendations
    
    def _analyze_existing_team(self, project) -> Dict:
        """
        Analisar time existente e sugerir melhorias.
        """
        team = project.team
        members = team.memberships.filter(is_active=True)
        
        analysis = {
            'team_size': members.count(),
            'roles_coverage': self._check_roles_coverage(members),
            'skill_coverage': self._check_skill_coverage(project, members),
            'recommendations': []
        }
        
        # Verificar tamanho do time
        if analysis['team_size'] < 3:
            analysis['recommendations'].append({
                'title': 'Time Muito Pequeno',
                'description': f'O time tem apenas {analysis["team_size"]} membros. Times ágeis funcionam melhor com 5-9 pessoas.',
                'confidence': 'high',
                'score': 0.3,
                'data': {'current_size': analysis['team_size'], 'recommended_min': 5}
            })
        elif analysis['team_size'] > 10:
            analysis['recommendations'].append({
                'title': 'Time Muito Grande',
                'description': f'O time tem {analysis["team_size"]} membros. Considere dividir em times menores.',
                'confidence': 'medium',
                'score': 0.6,
                'data': {'current_size': analysis['team_size'], 'recommended_max': 9}
            })
        
        # Verificar cobertura de papéis
        missing_roles = []
        if not analysis['roles_coverage'].get('has_po', False):
            missing_roles.append('Product Owner')
        if not analysis['roles_coverage'].get('has_sm', False):
            missing_roles.append('Scrum Master')
        
        if missing_roles:
            analysis['recommendations'].append({
                'title': 'Papéis Scrum Ausentes',
                'description': f'O time não possui: {", ".join(missing_roles)}. Considere designar membros para estes papéis.',
                'confidence': 'high',
                'score': 0.4,
                'data': {'missing_roles': missing_roles}
            })
        
        return analysis
    
    def _suggest_team_formation(self, project) -> List[Dict]:
        """
        Sugerir formação de time para projeto sem time.
        """
        from apps.accounts.models import User
        from apps.skills.models import UserSkill
        
        # Buscar usuários disponíveis
        available_users = User.objects.filter(
            is_available=True,
            is_active=True,
            role='collaborator'
        )
        
        # Calcular scores de compatibilidade
        user_scores = []
        for user in available_users:
            score = self._calculate_user_project_fit(user, project)
            if score > 0.3:  # Mínimo de 30% de compatibilidade
                user_scores.append({
                    'user': user,
                    'score': score,
                    'reasons': self._get_fit_reasons(user, project)
                })
        
        # Ordenar por score
        user_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Sugerir top 5 candidatos
        suggestions = []
        for candidate in user_scores[:5]:
            suggestions.append({
                'title': f'Candidato para o Time: {candidate["user"].get_full_name()}',
                'description': f"""
                {candidate["user"].get_full_name()} ({candidate["user"].position}) seria uma boa adição ao time.
                
                Score de compatibilidade: {candidate["score"]:.1f}/100
                
                Razões:
                {chr(10).join(f"- {reason}" for reason in candidate["reasons"])}
                """,
                'confidence': 'medium' if candidate['score'] > 0.7 else 'low',
                'score': candidate['score'],
                'data': {
                    'user_id': candidate['user'].id,
                    'reasons': candidate['reasons']
                }
            })
        
        return suggestions
    
    def _calculate_delay_risk(self, project) -> Dict:
        """
        Calcular risco de atraso do projeto.
        """
        from apps.tasks.models import Task
        
        total_tasks = project.tasks.count()
        if total_tasks == 0:
            return {'risk_level': 'low', 'risk_score': 0}
        
        # Métricas básicas
        completed_tasks = project.tasks.filter(status='done').count()
        overdue_tasks = project.tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        ).count()
        
        progress = (completed_tasks / total_tasks) * 100
        
        # Calcular velocity (simplificado)
        velocity = self._calculate_simple_velocity(project)
        
        # Calcular score de risco (0-1, onde 1 = alto risco)
        risk_factors = []
        
        # Fator 1: Tarefas em atraso
        overdue_factor = min(1.0, overdue_tasks / total_tasks * 2)
        risk_factors.append(overdue_factor)
        
        # Fator 2: Progresso baixo
        if progress < 30:
            progress_factor = 0.8
        elif progress < 60:
            progress_factor = 0.4
        else:
            progress_factor = 0.1
        risk_factors.append(progress_factor)
        
        # Fator 3: Velocity baixa
        if velocity < 5:
            velocity_factor = 0.7
        elif velocity < 10:
            velocity_factor = 0.3
        else:
            velocity_factor = 0.1
        risk_factors.append(velocity_factor)
        
        # Score final (média dos fatores)
        risk_score = sum(risk_factors) / len(risk_factors)
        
        # Determinar nível de risco
        if risk_score > 0.7:
            risk_level = 'high'
        elif risk_score > 0.4:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'overdue_tasks': overdue_tasks,
            'total_tasks': total_tasks,
            'progress': progress,
            'velocity': velocity,
            'factors': {
                'overdue_factor': overdue_factor,
                'progress_factor': progress_factor,
                'velocity_factor': velocity_factor
            }
        }
    
    def _analyze_scrum_roles(self, team) -> List[Dict]:
        """
        Analisar membros do time e sugerir papéis Scrum ideais.
        """
        from apps.skills.models import UserSkill
        
        members = team.memberships.filter(is_active=True)
        suggestions = []
        
        for membership in members:
            user = membership.user
            current_role = membership.role
            
            # Analisar skills do usuário
            user_skills = UserSkill.objects.filter(user=user)
            
            # Score para cada papel Scrum
            po_score = self._calculate_po_score(user, user_skills)
            sm_score = self._calculate_sm_score(user, user_skills)
            dev_score = self._calculate_dev_score(user, user_skills)
            
            # Determinar melhor papel
            scores = {
                'product_owner': po_score,
                'scrum_master': sm_score,
                'developer': dev_score
            }
            
            best_role = max(scores, key=scores.get)
            best_score = scores[best_role]
            
            # Se o score for significativamente melhor que o papel atual
            if best_role != current_role and best_score > 60:
                reasons = self._get_role_reasons(user, best_role, user_skills)
                
                suggestions.append({
                    'user': user,
                    'current_role': current_role,
                    'recommended_role': best_role,
                    'score': best_score,
                    'confidence': 'high' if best_score > 80 else 'medium',
                    'reasons': reasons
                })
        
        return suggestions
    
    def _calculate_po_score(self, user, user_skills) -> float:
        """Calcular score para Product Owner."""
        score = 0
        
        # Skills relevantes para PO
        po_skills = ['negocio', 'comunicacao', 'lideranca', 'analise']
        
        for skill in user_skills:
            if any(po_skill in skill.skill.name.lower() for po_skill in po_skills):
                score += skill.level * 10
        
        # Bonus se já é líder
        if user.is_leader():
            score += 20
        
        return min(100, score)
    
    def _calculate_sm_score(self, user, user_skills) -> float:
        """Calcular score para Scrum Master."""
        score = 0
        
        # Skills relevantes para SM
        sm_skills = ['agile', 'scrum', 'facilitacao', 'coaching', 'lideranca']
        
        for skill in user_skills:
            if any(sm_skill in skill.skill.name.lower() for sm_skill in sm_skills):
                score += skill.level * 12
        
        # Bonus para experiência
        if user.position and 'senior' in user.position.lower():
            score += 15
        
        return min(100, score)
    
    def _calculate_dev_score(self, user, user_skills) -> float:
        """Calcular score para Developer."""
        score = 0
        
        # Skills técnicas
        tech_skills = ['programacao', 'desenvolvimento', 'frontend', 'backend', 'mobile']
        
        for skill in user_skills:
            if any(tech_skill in skill.skill.name.lower() for tech_skill in tech_skills):
                score += skill.level * 15
        
        # Base score para todos
        score += 30
        
        return min(100, score)
    
    def _get_role_reasons(self, user, role, user_skills) -> List[str]:
        """Gerar razões para recomendação de papel."""
        reasons = []
        
        if role == 'product_owner':
            reasons.append("Possui habilidades de negócio e comunicação")
            if user.is_leader():
                reasons.append("Já possui experiência em liderança")
        
        elif role == 'scrum_master':
            reasons.append("Demonstra habilidades de facilitação e coaching")
            if user.position and 'senior' in user.position.lower():
                reasons.append("Experiência sênior adequada para mentoria")
        
        elif role == 'developer':
            reasons.append("Forte background técnico")
            reasons.append("Skills de desenvolvimento bem desenvolvidas")
        
        return reasons
    
    def _calculate_user_project_fit(self, user, project) -> float:
        """Calcular compatibilidade entre usuário e projeto."""
        # Implementação simplificada
        base_score = 0.5
        
        # Bonus por disponibilidade
        if user.is_available:
            base_score += 0.2
        
        # Bonus por skills (simulado)
        if hasattr(user, 'user_skills') and user.user_skills.count() > 0:
            base_score += 0.2
        
        # Bonus por experiência
        if user.position:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _get_fit_reasons(self, user, project) -> List[str]:
        """Gerar razões para compatibilidade usuário-projeto."""
        reasons = []
        
        if user.is_available:
            reasons.append("Disponível para alocação")
        
        if user.position:
            reasons.append(f"Experiência como {user.position}")
        
        if hasattr(user, 'user_skills') and user.user_skills.count() > 0:
            reasons.append("Possui skills relevantes cadastradas")
        
        return reasons
    
    def _check_roles_coverage(self, members) -> Dict:
        """Verificar cobertura de papéis no time."""
        roles = list(members.values_list('role', flat=True))
        
        return {
            'has_po': 'product_owner' in roles,
            'has_sm': 'scrum_master' in roles,
            'dev_count': roles.count('developer'),
            'roles_distribution': dict(Counter(roles))
        }
    
    def _check_skill_coverage(self, project, members) -> Dict:
        """Verificar cobertura de skills no time."""
        # Implementação simplificada
        return {
            'total_skills': 10,  # Simulado
            'covered_skills': 7,  # Simulado
            'coverage_percentage': 70
        }
    
    def _calculate_simple_velocity(self, project) -> float:
        """Calcular velocity simplificada do projeto."""
        from apps.tasks.models import Task
        
        # Contar tarefas concluídas nos últimos 7 dias
        recent_completed = project.tasks.filter(
            status='done',
            completed_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        
        return recent_completed
    
    def calculate_team_compatibility(self, team) -> Optional[float]:
        """Calcular score de compatibilidade do time."""
        members = team.memberships.filter(is_active=True)
        
        if members.count() < 2:
            return None
        
        # Score base
        compatibility_score = 0.6
        
        # Bonus por diversidade de skills
        total_skills = 0
        for member in members:
            if hasattr(member.user, 'user_skills'):
                total_skills += member.user.user_skills.count()
        
        if total_skills > members.count() * 2:
            compatibility_score += 0.2
        
        # Bonus por mix de seniority
        positions = [m.user.position for m in members if m.user.position]
        if len(set(positions)) > 1:
            compatibility_score += 0.1
        
        return min(1.0, compatibility_score)
    
    def calculate_skill_match_score(self, project) -> Optional[float]:
        """Calcular score de match de skills do time com projeto."""
        if not project.team:
            return None
        
        # Implementação simplificada
        # Em um sistema real, compararia skills do time com requisitos do projeto
        return random.uniform(0.6, 0.9)  # Score simulado