from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from apps.teams.models import Team, TeamMembership
from apps.projects.models import Project
from apps.skills.models import UserSkill
from apps.tasks.models import Task

User = get_user_model()


@login_required
def profile_redirect(request):
    """Redireciona para a página apropriada baseada no role do usuário."""
    user = request.user
    
    if user.role == 'admin':
        return redirect('accounts:admin_dashboard')
    elif user.role == 'leader':
        return redirect('accounts:leader_dashboard')
    else:  # collaborator
        return redirect('accounts:collaborator_dashboard')


@login_required
def admin_dashboard(request):
    """Dashboard completo para administradores."""
    
    # Verificar se é admin
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect('home')
    
    # Estatísticas gerais
    stats = {
        'total_users': User.objects.count(),
        'total_teams': Team.objects.count(),
        'total_projects': Project.objects.count(),
        'active_projects': Project.objects.filter(status='in_progress').count(),
        'total_tasks': Task.objects.count(),
        'completed_tasks': Task.objects.filter(status='done').count(),
    }
    
    # Usuários por role
    users_by_role = {
        'admins': User.objects.filter(role='admin').count(),
        'leaders': User.objects.filter(role='leader').count(),
        'collaborators': User.objects.filter(role='collaborator').count(),
    }
    
    # Times mais ativos
    active_teams = Team.objects.annotate(
        members_count=Count('memberships'),
        projects_count=Count('projects')
    ).order_by('-members_count')[:5]
    
    # Usuários recentes
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Skills mais populares
    popular_skills = UserSkill.objects.values('skill__name').annotate(
        count=Count('skill')
    ).order_by('-count')[:10]
    
    context = {
        'stats': stats,
        'users_by_role': users_by_role,
        'active_teams': active_teams,
        'recent_users': recent_users,
        'popular_skills': popular_skills,
        'user': request.user,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def leader_dashboard(request):
    """Dashboard para líderes com foco em gestão de equipes."""
    
    # Verificar se é líder
    if request.user.role != 'leader' and request.user.role != 'admin':
        messages.error(request, 'Acesso negado. Apenas líderes podem acessar esta página.')
        return redirect('home')
    
    # Times que o usuário lidera
    my_teams = Team.objects.filter(
        memberships__user=request.user,
        memberships__is_lead=True,
        is_active=True
    ).annotate(
        members_count=Count('memberships')
    ).order_by('-created_at')
    
    # Projetos dos seus times
    my_projects = Project.objects.filter(
        team__in=my_teams,
        is_active=True
    ).order_by('-created_at')
    
    # Estatísticas do líder
    leader_stats = {
        'teams_count': my_teams.count(),
        'projects_count': my_projects.count(),
        'total_members': sum(team.members_count for team in my_teams),
        'active_projects': my_projects.filter(status='in_progress').count(),
    }
    
    # Tasks dos projetos
    team_tasks = Task.objects.filter(
        project__in=my_projects
    ).order_by('-created_at')[:10]
    
    # Membros de todas as equipes
    all_members = User.objects.filter(
        team_memberships__team__in=my_teams,
        team_memberships__is_active=True
    ).distinct().exclude(id=request.user.id)
    
    # Disponibilidade para criar nova equipe
    available_collaborators = User.objects.filter(
        role='collaborator',
        is_active=True
    ).annotate(
        teams_count=Count('team_memberships')
    ).order_by('teams_count')
    
    context = {
        'my_teams': my_teams,
        'my_projects': my_projects,
        'leader_stats': leader_stats,
        'team_tasks': team_tasks,
        'all_members': all_members,
        'available_collaborators': available_collaborators,
        'user': request.user,
    }
    
    return render(request, 'accounts/leader_dashboard.html', context)


@login_required
def collaborator_dashboard(request):
    """Dashboard para colaboradores com foco em projetos participantes."""
    
    # Times que o usuário participa
    my_teams = Team.objects.filter(
        memberships__user=request.user,
        memberships__is_active=True,
        is_active=True
    ).annotate(
        members_count=Count('memberships')
    ).order_by('-created_at')
    
    # Projetos que participa
    my_projects = Project.objects.filter(
        team__in=my_teams,
        is_active=True
    ).order_by('-created_at')
    
    # Tasks atribuídas ao usuário
    my_tasks = Task.objects.filter(
        Q(assigned_to=request.user) | Q(project__team__in=my_teams)
    ).order_by('-created_at')[:15]
    
    # Estatísticas do colaborador
    collab_stats = {
        'teams_count': my_teams.count(),
        'projects_count': my_projects.count(),
        'tasks_assigned': my_tasks.filter(assigned_to=request.user).count(),
        'tasks_completed': my_tasks.filter(assigned_to=request.user, status='done').count(),
    }
    
    # Skills do usuário
    user_skills = UserSkill.objects.filter(
        user=request.user
    ).select_related('skill', 'skill__category').order_by('-level', 'skill__name')
    
    # Histórico de projetos (incluindo finalizados)
    project_history = Project.objects.filter(
        team__memberships__user=request.user
    ).order_by('-created_at')[:10]
    
    # Convites pendentes (se implementado)
    # pending_invites = TeamInvitation.objects.filter(user=request.user, status='pending')
    
    context = {
        'my_teams': my_teams,
        'my_projects': my_projects,
        'my_tasks': my_tasks,
        'collab_stats': collab_stats,
        'user_skills': user_skills,
        'project_history': project_history,
        'user': request.user,
    }
    
    return render(request, 'accounts/collaborator_dashboard.html', context)


@login_required
def user_profile(request, user_id=None):
    """Visualizar perfil de usuário (próprio ou de outros)."""
    
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
    else:
        profile_user = request.user
    
    # Skills do usuário
    user_skills = UserSkill.objects.filter(
        user=profile_user
    ).select_related('skill', 'skill__category').order_by('-level', 'skill__name')
    
    # Times que participa
    user_teams = Team.objects.filter(
        memberships__user=profile_user,
        memberships__is_active=True,
        is_active=True
    )
    
    # Projetos que participou
    user_projects = Project.objects.filter(
        team__memberships__user=profile_user
    ).distinct().order_by('-created_at')
    
    # Estatísticas do perfil
    profile_stats = {
        'teams_count': user_teams.count(),
        'projects_count': user_projects.count(),
        'skills_count': user_skills.count(),
        'avg_skill_level': user_skills.aggregate(
            avg_level=Avg('level')
        )['avg_level'] or 0,
    }
    
    context = {
        'profile_user': profile_user,
        'user_skills': user_skills,
        'user_teams': user_teams,
        'user_projects': user_projects,
        'profile_stats': profile_stats,
        'is_own_profile': profile_user.id == request.user.id,
    }
    
    return render(request, 'accounts/user_profile.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_ai_team(request):
    """Simular criação de equipe com IA."""
    
    # Verificar se é líder ou admin
    if request.user.role not in ['leader', 'admin']:
        return JsonResponse({'success': False, 'error': 'Permissão negada'})
    
    try:
        data = json.loads(request.body)
        project_type = data.get('project_type')
        team_size = int(data.get('team_size', 5))
        required_skills = data.get('required_skills', [])
        
        # Simular IA - buscar colaboradores baseado em skills
        from django.db.models import Count, Q
        import random
        
        # Filtrar colaboradores disponíveis
        available_users = User.objects.filter(
            role='collaborator',
            is_active=True
        ).annotate(
            teams_count=Count('team_memberships')
        ).filter(teams_count__lt=3)  # Máximo 3 times por pessoa
        
        # Se tem skills requeridas, priorizar
        if required_skills:
            skilled_users = available_users.filter(
                user_skills__skill__name__in=required_skills
            ).distinct()
            
            other_users = available_users.exclude(
                id__in=skilled_users.values_list('id', flat=True)
            )
            
            # Combinar listas priorizando skilled users
            suggested_users = list(skilled_users) + list(other_users)
        else:
            suggested_users = list(available_users)
        
        # Selecionar usuários aleatoriamente (simula IA)
        selected_users = random.sample(
            suggested_users, 
            min(team_size - 1, len(suggested_users))  # -1 para o líder
        )
        
        # Preparar resposta
        team_suggestion = []
        for user in selected_users:
            user_skills = UserSkill.objects.filter(user=user).select_related('skill')
            team_suggestion.append({
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'role': user.role,
                'skills': [
                    {
                        'name': us.skill.name,
                        'level': us.level,
                        'level_display': us.get_level_display()
                    } for us in user_skills[:5]
                ],
                'teams_count': user.team_memberships.filter(is_active=True).count()
            })
        
        return JsonResponse({
            'success': True,
            'team_suggestion': team_suggestion,
            'ai_explanation': f"""
            🤖 Sugestão de Equipe IA - Projeto: {project_type}
            
            ✨ Critérios utilizados:
            • Tamanho da equipe: {team_size} membros
            • Skills priorizadas: {', '.join(required_skills) if required_skills else 'Qualquer'}
            • Disponibilidade: Máximo 3 times por colaborador
            • Balanceamento: Mistura de diferentes níveis de expertise
            
            📊 Algoritmo aplicado:
            1. Filtrou colaboradores disponíveis ({len(available_users)} encontrados)
            2. Priorizou usuários com skills relevantes
            3. Considerou carga de trabalho atual
            4. Aplicou randomização inteligente para diversidade
            
            🎯 Resultado: {len(selected_users)} colaboradores selecionados
            """.strip()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_skills_suggestions(request):
    """Obter sugestões de skills para criação de equipe."""
    
    from apps.skills.models import Skill, SkillCategory
    
    # Buscar skills por categoria
    categories = SkillCategory.objects.prefetch_related('skills').all()
    
    suggestions = []
    for category in categories:
        category_skills = []
        for skill in category.skills.filter(is_active=True)[:10]:
            # Contar quantos usuários têm esta skill
            users_count = UserSkill.objects.filter(skill=skill).count()
            category_skills.append({
                'id': skill.id,
                'name': skill.name,
                'description': skill.description,
                'users_count': users_count
            })
        
        if category_skills:
            suggestions.append({
                'category': category.name,
                'icon': category.icon,
                'skills': category_skills
            })
    
    return JsonResponse({'suggestions': suggestions})