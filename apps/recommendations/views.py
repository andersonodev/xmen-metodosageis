from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Recommendation
from .serializers import RecommendationSerializer
from apps.tasks.models import Task
from apps.projects.models import Project
from apps.teams.models import Team, TeamMembership
from apps.skills.models import UserSkill
from apps.accounts.models import User


@extend_schema_view(
    list=extend_schema(tags=['Recommendations'], summary='Listar recommendations'),
    create=extend_schema(tags=['Recommendations'], summary='Criar recommendation'),
    retrieve=extend_schema(tags=['Recommendations'], summary='Detalhes do recommendation'),
    update=extend_schema(tags=['Recommendations'], summary='Atualizar recommendation'),
    destroy=extend_schema(tags=['Recommendations'], summary='Excluir recommendation'),
)
class RecommendationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar recommendations.
    """
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return Recommendation.objects.all()
        return self.queryset


@login_required
def recommendation_list(request):
    """
    Lista de recomendações personalizadas para o usuário.
    """
    # Generate mock recommendations based on real data
    recommendations = generate_smart_recommendations(request.user)
    
    # Separate by priority and recency
    priority_recommendations = [r for r in recommendations if r['priority'] == 'high'][:5]
    recent_recommendations = recommendations[:8]
    
    # Calculate statistics
    team_recommendations_count = len([r for r in recommendations if r['type'] == 'team'])
    skill_recommendations_count = len([r for r in recommendations if r['type'] == 'skill'])
    project_recommendations_count = len([r for r in recommendations if r['type'] == 'project'])
    improvement_recommendations_count = len([r for r in recommendations if r['type'] == 'improvement'])
    
    context = {
        'priority_recommendations': priority_recommendations,
        'recent_recommendations': recent_recommendations,
        'team_recommendations_count': team_recommendations_count,
        'skill_recommendations_count': skill_recommendations_count,
        'project_recommendations_count': project_recommendations_count,
        'improvement_recommendations_count': improvement_recommendations_count,
    }
    
    return render(request, 'recommendations/list.html', context)


def generate_smart_recommendations(user):
    """
    Gera recomendações inteligentes baseadas em dados reais do sistema.
    """
    recommendations = []
    
    # Análise de projetos - projetos onde o usuário é membro da equipe ou criador
    user_projects = Project.objects.filter(
        models.Q(team__memberships__user=user, team__memberships__is_active=True) |
        models.Q(created_by=user)
    ).distinct()
    
    overdue_projects = user_projects.filter(
        end_date__lt=timezone.now().date(),
        status__in=['planning', 'active']
    )
    
    if overdue_projects.exists():
        recommendations.append({
            'id': 1,
            'type': 'project',
            'priority': 'high',
            'title': 'Projetos com Atraso Detectados',
            'description': f'Há {overdue_projects.count()} projeto(s) com prazo vencido. Recomenda-se revisar cronogramas e realocar recursos.',
        })
    
    # Análise de tarefas
    user_tasks = Task.objects.filter(assignee=user)
    overdue_tasks = user_tasks.filter(
        due_date__lt=timezone.now(),
        status__in=['todo', 'in_progress']
    )
    
    if overdue_tasks.exists():
        recommendations.append({
            'id': 2,
            'type': 'improvement',
            'priority': 'high',
            'title': 'Tarefas em Atraso',
            'description': f'Você tem {overdue_tasks.count()} tarefa(s) em atraso. Considere repriorizar ou solicitar ajuda.',
        })
    
    # Análise de skills
    user_skills = UserSkill.objects.filter(user=user)
    low_skills = user_skills.filter(proficiency_level__lt=3)
    
    if low_skills.exists():
        recommendations.append({
            'id': 3,
            'type': 'skill',
            'priority': 'medium',
            'title': 'Oportunidades de Desenvolvimento',
            'description': f'Identificamos {low_skills.count()} skill(s) que podem ser melhoradas para aumentar sua eficiência.',
        })
    
    # Análise de equipe
    user_teams = Team.objects.filter(members=user)
    for team in user_teams:
        if team.members.count() < 3:
            recommendations.append({
                'id': 4,
                'type': 'team',
                'priority': 'low',
                'title': f'Equipe {team.name} Pequena',
                'description': 'Equipe com poucos membros pode impactar a produtividade. Considere adicionar mais colaboradores.',
            })
    
    # Recomendações baseadas em workload
    active_tasks_count = user_tasks.filter(status__in=['todo', 'in_progress']).count()
    
    if active_tasks_count > 10:
        recommendations.append({
            'id': 5,
            'type': 'improvement',
            'priority': 'medium',
            'title': 'Sobrecarga de Trabalho',
            'description': f'Você tem {active_tasks_count} tarefas ativas. Considere delegar ou repriorizar algumas.',
        })
    elif active_tasks_count < 3:
        recommendations.append({
            'id': 6,
            'type': 'improvement',
            'priority': 'low',
            'title': 'Capacidade Disponível',
            'description': 'Você tem capacidade disponível. Considere assumir mais responsabilidades ou ajudar colegas.',
        })
    
    # Recomendações de colaboração
    team_projects = user_projects.filter(status='active')
    if team_projects.exists():
        recommendations.append({
            'id': 7,
            'type': 'team',
            'priority': 'medium',
            'title': 'Oportunidade de Mentoria',
            'description': 'Seus projetos ativos podem se beneficiar de sessões de pair programming com membros júnior.',
        })
    
    # Recomendações de metodologia
    recommendations.append({
        'id': 8,
        'type': 'improvement',
        'priority': 'low',
        'title': 'Implementar Daily Standups',
        'description': 'Reuniões diárias podem melhorar a comunicação e identificar bloqueios mais rapidamente.',
    })
    
    return recommendations


@require_POST
@login_required
def apply_recommendation(request, recommendation_id):
    """
    Aplica uma recomendação (placeholder para ações futuras).
    """
    try:
        # Aqui você implementaria a lógica específica para cada tipo de recomendação
        # Por enquanto, apenas retornamos sucesso
        return JsonResponse({'success': True, 'message': 'Recomendação aplicada com sucesso!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
@login_required
def dismiss_recommendation(request, recommendation_id):
    """
    Dispensa uma recomendação.
    """
    try:
        # Aqui você salvaria que o usuário dispensou esta recomendação
        # Para não mostrar novamente
        return JsonResponse({'success': True, 'message': 'Recomendação dispensada!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def recommendation_detail(request, recommendation_id):
    """
    Detalhes de uma recomendação específica.
    """
    # Placeholder para futuras implementações
    context = {
        'recommendation_id': recommendation_id,
    }
    return render(request, 'recommendations/detail.html', context)

