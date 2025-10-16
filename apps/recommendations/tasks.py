from celery import shared_task
from django.utils import timezone
import random


@shared_task
def generate_recommendations():
    """
    Gerar recomendações para todos os projetos ativos.
    """
    from apps.projects.models import Project
    from apps.recommendations.service import RecommendationService
    
    active_projects = Project.objects.filter(status='active')
    recommendations_generated = 0
    
    service = RecommendationService()
    
    for project in active_projects:
        # Gerar recomendações de alocação de time
        team_recs = service.get_team_allocation_recommendations(project)
        recommendations_generated += len(team_recs)
        
        # Gerar análise de risco de atraso
        delay_recs = service.get_delay_risk_recommendations(project)
        recommendations_generated += len(delay_recs)
        
        # Gerar sugestões de papéis Scrum
        role_recs = service.get_scrum_role_recommendations(project)
        recommendations_generated += len(role_recs)
    
    return f"Geradas {recommendations_generated} recomendações"


@shared_task
def analyze_team_compatibility():
    """
    Analisar compatibilidade entre membros dos times.
    """
    from apps.teams.models import Team
    from apps.recommendations.service import RecommendationService
    
    active_teams = Team.objects.filter(is_active=True)
    analyses_created = 0
    
    service = RecommendationService()
    
    for team in active_teams:
        compatibility_score = service.calculate_team_compatibility(team)
        if compatibility_score is not None:
            analyses_created += 1
    
    return f"Analisadas {analyses_created} compatibilidades de times"


@shared_task
def update_skill_match_scores():
    """
    Atualizar scores de match de skills para projetos.
    """
    from apps.projects.models import Project
    from apps.recommendations.service import RecommendationService
    
    projects_with_teams = Project.objects.filter(
        status='active',
        team__isnull=False
    )
    scores_updated = 0
    
    service = RecommendationService()
    
    for project in projects_with_teams:
        match_score = service.calculate_skill_match_score(project)
        if match_score is not None:
            scores_updated += 1
    
    return f"Atualizados {scores_updated} scores de match de skills"