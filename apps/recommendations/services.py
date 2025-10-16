"""
Serviços de IA para recomendações inteligentes
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.accounts.models import User
from apps.skills.models import UserSkill, Skill
from apps.teams.models import Team, TeamMembership
from apps.projects.models import Project, Sprint
from apps.tasks.models import Task
from apps.dashboards.models import MetricsSnapshot


class TeamAllocationService:
    """Serviço para recomendação de alocação de equipes"""
    
    @staticmethod
    def recommend_team(project_id: int, required_skills: List[Dict], team_size: int, **kwargs) -> Dict[str, Any]:
        """
        Recomenda uma equipe baseada nas habilidades necessárias
        """
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return {"error": "Projeto não encontrado"}
        
        # Buscar usuários disponíveis
        exclude_users = kwargs.get('exclude_users', [])
        available_users = User.objects.filter(
            is_active=True,
            role__in=['COLLABORATOR', 'LEADER']
        ).exclude(id__in=exclude_users)
        
        # Calcular scores para cada usuário
        user_scores = []
        for user in available_users:
            score = TeamAllocationService._calculate_user_score(user, required_skills)
            if score > 0:
                user_scores.append({
                    'user_id': user.id,
                    'user_name': user.get_full_name(),
                    'email': user.email,
                    'score': score,
                    'skills_match': TeamAllocationService._get_user_skills_match(user, required_skills),
                    'experience_years': user.experience_years or 0,
                    'availability': TeamAllocationService._check_user_availability(user)
                })
        
        # Ordenar por score e selecionar os melhores
        user_scores.sort(key=lambda x: x['score'], reverse=True)
        recommended_team = user_scores[:team_size]
        
        # Calcular métricas da recomendação
        confidence_score = TeamAllocationService._calculate_confidence(recommended_team, required_skills)
        skill_coverage = TeamAllocationService._calculate_skill_coverage(recommended_team, required_skills)
        
        return {
            'recommended_team': recommended_team,
            'confidence_score': confidence_score,
            'skill_coverage': skill_coverage,
            'alternative_teams': user_scores[team_size:team_size*2] if len(user_scores) > team_size else [],
            'reasoning': TeamAllocationService._generate_reasoning(recommended_team, required_skills)
        }
    
    @staticmethod
    def _calculate_user_score(user: User, required_skills: List[Dict]) -> float:
        """Calcula score do usuário baseado nas habilidades necessárias"""
        user_skills = UserSkill.objects.filter(user=user, is_active=True)
        total_score = 0
        max_possible_score = 0
        
        for req_skill in required_skills:
            skill_id = req_skill.get('skill_id')
            required_level = req_skill.get('level', 'JUNIOR')
            
            max_possible_score += 100
            
            # Procurar skill do usuário
            user_skill = user_skills.filter(skill_id=skill_id).first()
            if user_skill:
                # Mapear níveis para pontuação
                level_scores = {'JUNIOR': 25, 'PLENO': 50, 'SENIOR': 75, 'SPECIALIST': 100}
                required_score = level_scores.get(required_level, 25)
                user_score = level_scores.get(user_skill.proficiency_level, 0)
                
                # Bonificar se usuário tem nível igual ou superior
                if user_score >= required_score:
                    total_score += 100
                elif user_score > 0:
                    total_score += (user_score / required_score) * 60
        
        return (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
    
    @staticmethod
    def _get_user_skills_match(user: User, required_skills: List[Dict]) -> List[Dict]:
        """Retorna as skills do usuário que fazem match com as necessárias"""
        matches = []
        user_skills = UserSkill.objects.filter(user=user, is_active=True).select_related('skill')
        
        for req_skill in required_skills:
            skill_id = req_skill.get('skill_id')
            user_skill = user_skills.filter(skill_id=skill_id).first()
            
            if user_skill:
                matches.append({
                    'skill_name': user_skill.skill.name,
                    'required_level': req_skill.get('level', 'JUNIOR'),
                    'user_level': user_skill.proficiency_level,
                    'is_match': True
                })
        
        return matches
    
    @staticmethod
    def _check_user_availability(user: User) -> Dict[str, Any]:
        """Verifica disponibilidade do usuário"""
        # Contar projetos ativos
        active_projects = Project.objects.filter(
            team__memberships__user=user,
            status='ACTIVE'
        ).count()
        
        # Calcular carga de trabalho (simulada)
        workload = min(active_projects * 25, 100)  # 25% por projeto, máximo 100%
        
        return {
            'active_projects': active_projects,
            'workload_percentage': workload,
            'is_available': workload < 80
        }
    
    @staticmethod
    def _calculate_confidence(team: List[Dict], required_skills: List[Dict]) -> float:
        """Calcula confiança na recomendação"""
        if not team:
            return 0.0
        
        avg_score = sum(member['score'] for member in team) / len(team)
        skill_coverage = len([s for s in required_skills if any(
            match['skill_name'] in str(member.get('skills_match', [])) 
            for member in team for match in member.get('skills_match', [])
        )]) / len(required_skills) if required_skills else 0
        
        return min((avg_score + skill_coverage * 50) / 100, 1.0)
    
    @staticmethod
    def _calculate_skill_coverage(team: List[Dict], required_skills: List[Dict]) -> Dict[str, Any]:
        """Calcula cobertura de habilidades"""
        covered_skills = set()
        total_skills = len(required_skills)
        
        for member in team:
            for match in member.get('skills_match', []):
                covered_skills.add(match['skill_name'])
        
        coverage_percentage = (len(covered_skills) / total_skills * 100) if total_skills > 0 else 0
        
        return {
            'covered_skills': list(covered_skills),
            'missing_skills': [
                skill for skill in required_skills 
                if not any(match['skill_name'] for member in team for match in member.get('skills_match', []))
            ],
            'coverage_percentage': round(coverage_percentage, 1)
        }
    
    @staticmethod
    def _generate_reasoning(team: List[Dict], required_skills: List[Dict]) -> str:
        """Gera explicação da recomendação"""
        if not team:
            return "Nenhum membro adequado encontrado para a equipe."
        
        avg_score = sum(member['score'] for member in team) / len(team)
        top_member = max(team, key=lambda x: x['score'])
        
        reasoning = f"Equipe recomendada com score médio de {avg_score:.1f}%. "
        reasoning += f"Destaque para {top_member['user_name']} com {top_member['score']:.1f}% de compatibilidade. "
        
        # Analisar disponibilidade
        available_count = sum(1 for member in team if member.get('availability', {}).get('is_available', False))
        if available_count == len(team):
            reasoning += "Todos os membros têm disponibilidade adequada."
        elif available_count > len(team) / 2:
            reasoning += f"{available_count}/{len(team)} membros têm disponibilidade adequada."
        else:
            reasoning += "Atenção: alguns membros podem ter alta carga de trabalho."
        
        return reasoning


class DelayRiskAnalysisService:
    """Serviço para análise de risco de atraso"""
    
    @staticmethod
    def analyze_delay_risk(project_id: int, **kwargs) -> Dict[str, Any]:
        """Analisa o risco de atraso de um projeto"""
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return {"error": "Projeto não encontrado"}
        
        current_sprint_id = kwargs.get('current_sprint_id')
        factors_to_analyze = kwargs.get('factors_to_analyze', ['velocity', 'burndown', 'team_capacity'])
        
        # Analisar fatores de risco
        risk_factors = []
        total_risk_score = 0
        
        for factor in factors_to_analyze:
            factor_analysis = DelayRiskAnalysisService._analyze_factor(project, factor, current_sprint_id)
            risk_factors.append(factor_analysis)
            total_risk_score += factor_analysis['risk_score']
        
        # Calcular risco geral
        avg_risk_score = total_risk_score / len(factors_to_analyze) if factors_to_analyze else 0
        risk_level = DelayRiskAnalysisService._calculate_risk_level(avg_risk_score)
        
        # Gerar recomendações
        recommendations = DelayRiskAnalysisService._generate_recommendations(risk_factors, risk_level)
        
        # Estimar dias de atraso
        estimated_delay = DelayRiskAnalysisService._estimate_delay_days(project, avg_risk_score)
        
        return {
            'risk_level': risk_level,
            'risk_percentage': round(avg_risk_score, 1),
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'estimated_delay_days': estimated_delay,
            'confidence': min(0.7 + (len(factors_to_analyze) * 0.1), 0.95)
        }
    
    @staticmethod
    def _analyze_factor(project: Project, factor: str, current_sprint_id: int = None) -> Dict[str, Any]:
        """Analisa um fator específico de risco"""
        if factor == 'velocity':
            return DelayRiskAnalysisService._analyze_velocity(project)
        elif factor == 'burndown':
            return DelayRiskAnalysisService._analyze_burndown(project, current_sprint_id)
        elif factor == 'team_capacity':
            return DelayRiskAnalysisService._analyze_team_capacity(project)
        elif factor == 'complexity':
            return DelayRiskAnalysisService._analyze_complexity(project)
        else:
            return {'factor': factor, 'risk_score': 0, 'description': 'Fator não reconhecido'}
    
    @staticmethod
    def _analyze_velocity(project: Project) -> Dict[str, Any]:
        """Analisa a velocidade da equipe"""
        # Buscar métricas recentes
        recent_metrics = MetricsSnapshot.objects.filter(
            project=project,
            date__gte=timezone.now() - timedelta(days=60)
        ).order_by('-date')[:5]
        
        if not recent_metrics:
            return {
                'factor': 'velocity',
                'risk_score': 30,
                'description': 'Sem dados de velocidade suficientes',
                'details': 'Histórico insuficiente para análise'
            }
        
        velocities = [m.velocity for m in recent_metrics if m.velocity]
        if not velocities:
            return {
                'factor': 'velocity',
                'risk_score': 40,
                'description': 'Velocidade não mensurada',
                'details': 'Necessário acompanhar story points'
            }
        
        avg_velocity = sum(velocities) / len(velocities)
        velocity_trend = DelayRiskAnalysisService._calculate_trend(velocities)
        
        # Calcular risco baseado na tendência
        if velocity_trend < -0.2:  # Queda de 20%+
            risk_score = 80
            description = "Velocidade em queda acentuada"
        elif velocity_trend < -0.1:  # Queda de 10%+
            risk_score = 60
            description = "Velocidade em declínio"
        elif velocity_trend > 0.1:  # Aumento de 10%+
            risk_score = 20
            description = "Velocidade em crescimento"
        else:
            risk_score = 40
            description = "Velocidade estável"
        
        return {
            'factor': 'velocity',
            'risk_score': risk_score,
            'description': description,
            'details': f'Velocidade média: {avg_velocity:.1f}, Tendência: {velocity_trend:.1%}'
        }
    
    @staticmethod
    def _analyze_burndown(project: Project, current_sprint_id: int = None) -> Dict[str, Any]:
        """Analisa o burndown do projeto/sprint"""
        if current_sprint_id:
            try:
                sprint = Sprint.objects.get(id=current_sprint_id)
                tasks = Task.objects.filter(column__board__project=project)
                # Análise específica do sprint
            except Sprint.DoesNotExist:
                pass
        
        # Análise geral do projeto
        total_tasks = Task.objects.filter(column__board__project=project).count()
        completed_tasks = Task.objects.filter(
            column__board__project=project,
            status='DONE'
        ).count()
        
        if total_tasks == 0:
            return {
                'factor': 'burndown',
                'risk_score': 50,
                'description': 'Projeto sem tarefas definidas',
                'details': 'Necessário criar backlog'
            }
        
        completion_rate = completed_tasks / total_tasks
        
        # Calcular dias desde início do projeto
        days_since_start = (timezone.now().date() - project.start_date).days if project.start_date else 0
        project_duration = (project.end_date - project.start_date).days if project.end_date and project.start_date else 100
        
        expected_completion = days_since_start / project_duration if project_duration > 0 else 0
        
        # Calcular risco baseado no desvio
        deviation = expected_completion - completion_rate
        
        if deviation > 0.3:  # 30% atrasado
            risk_score = 90
            description = "Muito atrasado em relação ao cronograma"
        elif deviation > 0.15:  # 15% atrasado
            risk_score = 70
            description = "Atrasado em relação ao cronograma"
        elif deviation > 0:
            risk_score = 50
            description = "Ligeiramente atrasado"
        else:
            risk_score = 30
            description = "No prazo ou adiantado"
        
        return {
            'factor': 'burndown',
            'risk_score': risk_score,
            'description': description,
            'details': f'Concluído: {completion_rate:.1%}, Esperado: {expected_completion:.1%}'
        }
    
    @staticmethod
    def _analyze_team_capacity(project: Project) -> Dict[str, Any]:
        """Analisa a capacidade da equipe"""
        if not project.team:
            return {
                'factor': 'team_capacity',
                'risk_score': 80,
                'description': 'Projeto sem equipe atribuída',
                'details': 'Necessário atribuir equipe ao projeto'
            }
        
        team_members = TeamMembership.objects.filter(
            team=project.team,
            is_active=True
        )
        
        if team_members.count() < 3:
            risk_score = 70
            description = "Equipe muito pequena"
        elif team_members.count() > 12:
            risk_score = 60
            description = "Equipe muito grande"
        else:
            risk_score = 30
            description = "Tamanho de equipe adequado"
        
        # Analisar carga de trabalho dos membros
        overloaded_members = 0
        for member in team_members:
            user_projects = Project.objects.filter(
                team__memberships__user=member.user,
                status='ACTIVE'
            ).count()
            if user_projects > 2:
                overloaded_members += 1
        
        if overloaded_members > team_members.count() / 2:
            risk_score += 20
            description += " com sobrecarga"
        
        return {
            'factor': 'team_capacity',
            'risk_score': min(risk_score, 100),
            'description': description,
            'details': f'{team_members.count()} membros, {overloaded_members} sobrecarregados'
        }
    
    @staticmethod
    def _analyze_complexity(project: Project) -> Dict[str, Any]:
        """Analisa a complexidade do projeto"""
        total_tasks = Task.objects.filter(column__board__project=project).count()
        high_priority_tasks = Task.objects.filter(
            column__board__project=project,
            priority='HIGH'
        ).count()
        
        if total_tasks == 0:
            return {
                'factor': 'complexity',
                'risk_score': 40,
                'description': 'Complexidade não avaliada',
                'details': 'Sem tarefas para análise'
            }
        
        high_priority_ratio = high_priority_tasks / total_tasks
        
        # Estimar complexidade baseada em story points médios
        avg_story_points = Task.objects.filter(
            column__board__project=project,
            story_points__isnull=False
        ).aggregate(avg_points=Avg('story_points'))['avg_points'] or 3
        
        complexity_score = 0
        if avg_story_points > 8:
            complexity_score += 30
        elif avg_story_points > 5:
            complexity_score += 20
        else:
            complexity_score += 10
        
        if high_priority_ratio > 0.5:
            complexity_score += 40
        elif high_priority_ratio > 0.3:
            complexity_score += 20
        else:
            complexity_score += 10
        
        if total_tasks > 100:
            complexity_score += 30
        elif total_tasks > 50:
            complexity_score += 20
        
        if complexity_score > 70:
            description = "Projeto de alta complexidade"
        elif complexity_score > 40:
            description = "Projeto de complexidade média"
        else:
            description = "Projeto de baixa complexidade"
        
        return {
            'factor': 'complexity',
            'risk_score': complexity_score,
            'description': description,
            'details': f'{total_tasks} tarefas, {high_priority_ratio:.1%} alta prioridade'
        }
    
    @staticmethod
    def _calculate_trend(values: List[float]) -> float:
        """Calcula tendência de uma série de valores"""
        if len(values) < 2:
            return 0
        return (values[-1] - values[0]) / values[0] if values[0] != 0 else 0
    
    @staticmethod
    def _calculate_risk_level(risk_score: float) -> str:
        """Determina o nível de risco baseado no score"""
        if risk_score >= 80:
            return 'CRITICAL'
        elif risk_score >= 60:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    @staticmethod
    def _generate_recommendations(risk_factors: List[Dict], risk_level: str) -> List[str]:
        """Gera recomendações baseadas nos fatores de risco"""
        recommendations = []
        
        for factor in risk_factors:
            if factor['risk_score'] > 60:
                if factor['factor'] == 'velocity':
                    recommendations.append("Revisar impedimentos que afetam a velocidade da equipe")
                    recommendations.append("Considerar ajustar scope ou adicionar recursos")
                elif factor['factor'] == 'burndown':
                    recommendations.append("Repriorizar tarefas críticas")
                    recommendations.append("Aumentar frequência de dailies")
                elif factor['factor'] == 'team_capacity':
                    recommendations.append("Redistribuir carga de trabalho")
                    recommendations.append("Considerar realocação de membros")
                elif factor['factor'] == 'complexity':
                    recommendations.append("Quebrar tarefas complexas em subtarefas")
                    recommendations.append("Alocar especialistas para tarefas críticas")
        
        if risk_level == 'CRITICAL':
            recommendations.append("Urgente: Revisar cronograma e escopo do projeto")
            recommendations.append("Considerar apoio executivo")
        elif risk_level == 'HIGH':
            recommendations.append("Agendar reunião de mitigação de riscos")
        
        return recommendations
    
    @staticmethod
    def _estimate_delay_days(project: Project, risk_score: float) -> int:
        """Estima dias de atraso baseado no score de risco"""
        if not project.end_date or not project.start_date:
            return 0
        
        project_duration = (project.end_date - project.start_date).days
        delay_factor = (risk_score - 30) / 100  # Risco acima de 30% pode causar atraso
        
        if delay_factor <= 0:
            return 0
        
        estimated_delay = int(project_duration * delay_factor * 0.3)  # Máximo 30% do projeto
        return min(estimated_delay, project_duration // 2)  # Limite de 50% da duração


class ScrumRoleRecommendationService:
    """Serviço para recomendação de papéis Scrum"""
    
    @staticmethod
    def recommend_scrum_roles(team_id: int, **kwargs) -> Dict[str, Any]:
        """Recomenda papéis Scrum para membros da equipe"""
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return {"error": "Equipe não encontrada"}
        
        project_id = kwargs.get('project_id')
        analyze_soft_skills = kwargs.get('analyze_soft_skills', True)
        consider_experience = kwargs.get('consider_experience', True)
        
        team_members = TeamMembership.objects.filter(
            team=team,
            is_active=True
        ).select_related('user')
        
        if not team_members:
            return {"error": "Equipe sem membros ativos"}
        
        recommendations = []
        
        # Analisar cada membro para cada papel
        for member in team_members:
            user_analysis = ScrumRoleRecommendationService._analyze_user_for_roles(
                member.user,
                analyze_soft_skills,
                consider_experience
            )
            recommendations.append({
                'user_id': member.user.id,
                'user_name': member.user.get_full_name(),
                'current_role': member.role,
                'recommended_roles': user_analysis['roles'],
                'strengths': user_analysis['strengths'],
                'development_areas': user_analysis['development_areas']
            })
        
        # Gerar atribuições alternativas
        alternative_assignments = ScrumRoleRecommendationService._generate_alternative_assignments(recommendations)
        
        # Gerar reasoning
        reasoning = ScrumRoleRecommendationService._generate_role_reasoning(recommendations, team_members.count())
        
        return {
            'recommendations': recommendations,
            'alternative_assignments': alternative_assignments,
            'reasoning': reasoning
        }
    
    @staticmethod
    def _analyze_user_for_roles(user: User, analyze_soft_skills: bool, consider_experience: bool) -> Dict[str, Any]:
        """Analisa um usuário para diferentes papéis Scrum"""
        user_skills = UserSkill.objects.filter(user=user, is_active=True).select_related('skill')
        
        # Mapear habilidades por categoria
        technical_skills = user_skills.filter(skill__category__name__icontains='técnica')
        leadership_skills = user_skills.filter(skill__category__name__icontains='liderança')
        communication_skills = user_skills.filter(skill__category__name__icontains='comunicação')
        
        roles_analysis = {
            'SCRUM_MASTER': ScrumRoleRecommendationService._analyze_for_scrum_master(
                user, leadership_skills, communication_skills, consider_experience
            ),
            'PRODUCT_OWNER': ScrumRoleRecommendationService._analyze_for_product_owner(
                user, leadership_skills, communication_skills, consider_experience
            ),
            'DEVELOPER': ScrumRoleRecommendationService._analyze_for_developer(
                user, technical_skills, consider_experience
            ),
            'TECH_LEAD': ScrumRoleRecommendationService._analyze_for_tech_lead(
                user, technical_skills, leadership_skills, consider_experience
            )
        }
        
        # Ordenar por score
        sorted_roles = sorted(roles_analysis.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Identificar pontos fortes e áreas de desenvolvimento
        strengths = []
        development_areas = []
        
        for role, analysis in sorted_roles:
            if analysis['score'] > 70:
                strengths.append(f"Forte candidato para {role}: {analysis['reasoning']}")
            elif analysis['score'] < 40:
                development_areas.append(f"Desenvolver para {role}: {analysis['reasoning']}")
        
        return {
            'roles': [{'role': role, **analysis} for role, analysis in sorted_roles],
            'strengths': strengths,
            'development_areas': development_areas
        }
    
    @staticmethod
    def _analyze_for_scrum_master(user: User, leadership_skills, communication_skills, consider_experience: bool) -> Dict[str, Any]:
        """Analisa adequação para Scrum Master"""
        score = 40  # Score base
        
        # Analisar habilidades de liderança
        if leadership_skills.filter(proficiency_level__in=['SENIOR', 'SPECIALIST']).exists():
            score += 25
        elif leadership_skills.exists():
            score += 15
        
        # Analisar habilidades de comunicação
        if communication_skills.filter(proficiency_level__in=['SENIOR', 'SPECIALIST']).exists():
            score += 25
        elif communication_skills.exists():
            score += 15
        
        # Experiência
        if consider_experience and user.experience_years:
            if user.experience_years >= 5:
                score += 15
            elif user.experience_years >= 3:
                score += 10
        
        # Role atual
        if user.role == 'LEADER':
            score += 10
        
        reasoning = f"Habilidades de liderança: {leadership_skills.count()}, "
        reasoning += f"Comunicação: {communication_skills.count()}, "
        reasoning += f"Experiência: {user.experience_years or 0} anos"
        
        return {'score': min(score, 100), 'reasoning': reasoning}
    
    @staticmethod
    def _analyze_for_product_owner(user: User, leadership_skills, communication_skills, consider_experience: bool) -> Dict[str, Any]:
        """Analisa adequação para Product Owner"""
        score = 35  # Score base
        
        # Analisar habilidades de liderança e negócio
        business_skills = leadership_skills.filter(
            skill__name__icontains__in=['produto', 'negócio', 'estratégia']
        )
        
        if business_skills.exists():
            score += 30
        elif leadership_skills.exists():
            score += 20
        
        # Comunicação
        if communication_skills.filter(proficiency_level__in=['SENIOR', 'SPECIALIST']).exists():
            score += 20
        elif communication_skills.exists():
            score += 10
        
        # Experiência
        if consider_experience and user.experience_years:
            if user.experience_years >= 4:
                score += 15
        
        # Role atual
        if user.role == 'LEADER':
            score += 15
        
        reasoning = f"Skills de negócio: {business_skills.count()}, "
        reasoning += f"Liderança: {leadership_skills.count()}, "
        reasoning += f"Comunicação: {communication_skills.count()}"
        
        return {'score': min(score, 100), 'reasoning': reasoning}
    
    @staticmethod
    def _analyze_for_developer(user: User, technical_skills, consider_experience: bool) -> Dict[str, Any]:
        """Analisa adequação para Developer"""
        score = 50  # Score base alto para desenvolvedor
        
        # Habilidades técnicas
        if technical_skills.filter(proficiency_level__in=['SENIOR', 'SPECIALIST']).count() >= 3:
            score += 30
        elif technical_skills.filter(proficiency_level__in=['PLENO', 'SENIOR']).count() >= 2:
            score += 20
        elif technical_skills.exists():
            score += 10
        
        # Experiência técnica
        if consider_experience and user.experience_years:
            if user.experience_years >= 3:
                score += 15
            elif user.experience_years >= 1:
                score += 10
        
        reasoning = f"Skills técnicas: {technical_skills.count()}, "
        reasoning += f"Experiência: {user.experience_years or 0} anos"
        
        return {'score': min(score, 100), 'reasoning': reasoning}
    
    @staticmethod
    def _analyze_for_tech_lead(user: User, technical_skills, leadership_skills, consider_experience: bool) -> Dict[str, Any]:
        """Analisa adequação para Tech Lead"""
        score = 30  # Score base
        
        # Combinar habilidades técnicas e liderança
        if (technical_skills.filter(proficiency_level__in=['SENIOR', 'SPECIALIST']).count() >= 2 and
            leadership_skills.exists()):
            score += 40
        elif technical_skills.filter(proficiency_level__in=['SENIOR', 'SPECIALIST']).exists():
            score += 25
        elif technical_skills.count() >= 3:
            score += 15
        
        # Liderança técnica
        if leadership_skills.exists():
            score += 20
        
        # Experiência sênior
        if consider_experience and user.experience_years:
            if user.experience_years >= 5:
                score += 20
            elif user.experience_years >= 3:
                score += 10
        
        reasoning = f"Skills técnicas sênior: {technical_skills.filter(proficiency_level__in=['SENIOR', 'SPECIALIST']).count()}, "
        reasoning += f"Liderança: {leadership_skills.count()}, "
        reasoning += f"Experiência: {user.experience_years or 0} anos"
        
        return {'score': min(score, 100), 'reasoning': reasoning}
    
    @staticmethod
    def _generate_alternative_assignments(recommendations: List[Dict]) -> List[Dict]:
        """Gera atribuições alternativas para a equipe"""
        alternatives = []
        
        # Encontrar melhor Scrum Master
        best_sm = max(recommendations, key=lambda x: next(
            (role['score'] for role in x['recommended_roles'] if role['role'] == 'SCRUM_MASTER'), 0
        ))
        
        # Encontrar melhor Product Owner
        best_po = max(recommendations, key=lambda x: next(
            (role['score'] for role in x['recommended_roles'] if role['role'] == 'PRODUCT_OWNER'), 0
        ))
        
        # Organização sugerida
        alternatives.append({
            'assignment_name': 'Configuração Recomendada',
            'assignments': [
                {
                    'user_name': best_sm['user_name'],
                    'suggested_role': 'SCRUM_MASTER',
                    'confidence': next((role['score'] for role in best_sm['recommended_roles'] if role['role'] == 'SCRUM_MASTER'), 0)
                },
                {
                    'user_name': best_po['user_name'],
                    'suggested_role': 'PRODUCT_OWNER',
                    'confidence': next((role['score'] for role in best_po['recommended_roles'] if role['role'] == 'PRODUCT_OWNER'), 0)
                }
            ]
        })
        
        return alternatives
    
    @staticmethod
    def _generate_role_reasoning(recommendations: List[Dict], team_size: int) -> Dict[str, Any]:
        """Gera reasoning para as recomendações de papéis"""
        role_distribution = {}
        for rec in recommendations:
            best_role = rec['recommended_roles'][0]['role'] if rec['recommended_roles'] else 'DEVELOPER'
            role_distribution[best_role] = role_distribution.get(best_role, 0) + 1
        
        analysis = f"Equipe de {team_size} membros. "
        analysis += f"Distribuição sugerida: {role_distribution}. "
        
        if role_distribution.get('SCRUM_MASTER', 0) == 0:
            analysis += "Atenção: Nenhum membro com forte perfil para Scrum Master. "
        
        if role_distribution.get('PRODUCT_OWNER', 0) == 0:
            analysis += "Atenção: Nenhum membro com forte perfil para Product Owner. "
        
        if role_distribution.get('DEVELOPER', 0) < team_size // 2:
            analysis += "Time com poucos desenvolvedores. "
        
        return {
            'team_analysis': analysis,
            'role_distribution': role_distribution,
            'recommendations_summary': f"Baseado em habilidades e experiência de {team_size} membros"
        }