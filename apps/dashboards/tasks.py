from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import json


@shared_task
def recalc_project_metrics():
    """
    Recalcular métricas de todos os projetos ativos.
    """
    from apps.projects.models import Project
    from apps.dashboards.models import MetricSnapshot
    
    active_projects = Project.objects.filter(status='active')
    metrics_updated = 0
    
    for project in active_projects:
        # Calcular velocity
        velocity = calculate_project_velocity(project)
        if velocity is not None:
            MetricSnapshot.objects.update_or_create(
                project=project,
                metric_type='velocity',
                period=f"{timezone.now().strftime('%Y-%m')}",
                defaults={
                    'value': velocity['value'],
                    'data': velocity['data']
                }
            )
            metrics_updated += 1
        
        # Calcular burndown
        burndown = calculate_project_burndown(project)
        if burndown is not None:
            MetricSnapshot.objects.update_or_create(
                project=project,
                metric_type='burndown',
                period=f"{timezone.now().strftime('%Y-%m')}",
                defaults={
                    'value': burndown['value'],
                    'data': burndown['data']
                }
            )
            metrics_updated += 1
    
    return f"Atualizadas {metrics_updated} métricas de projetos"


def calculate_project_velocity(project):
    """
    Calcular velocity média do projeto baseado nos últimos sprints.
    """
    from apps.projects.models import Sprint
    
    # Pegar últimos 3 sprints concluídos
    sprints = Sprint.objects.filter(
        project=project,
        status='completed'
    ).order_by('-end_date')[:3]
    
    if not sprints:
        return None
    
    total_points = sum(sprint.completed_points for sprint in sprints)
    avg_velocity = total_points / len(sprints)
    
    sprint_data = []
    for sprint in sprints:
        sprint_data.append({
            'sprint_name': sprint.name,
            'completed_points': sprint.completed_points,
            'planned_points': sprint.planned_points,
            'end_date': sprint.end_date.isoformat()
        })
    
    return {
        'value': avg_velocity,
        'data': {
            'sprints_analyzed': len(sprints),
            'total_points': total_points,
            'sprint_details': sprint_data
        }
    }


def calculate_project_burndown(project):
    """
    Calcular burndown atual do projeto.
    """
    from apps.tasks.models import Task
    
    total_tasks = project.tasks.count()
    if total_tasks == 0:
        return None
    
    completed_tasks = project.tasks.filter(status='done').count()
    remaining_tasks = total_tasks - completed_tasks
    
    # Calcular progresso por dia nos últimos 30 dias
    daily_progress = []
    for i in range(30, 0, -1):
        date = timezone.now().date() - timedelta(days=i)
        completed_by_date = project.tasks.filter(
            status='done',
            completed_at__date__lte=date
        ).count()
        remaining_by_date = total_tasks - completed_by_date
        
        daily_progress.append({
            'date': date.isoformat(),
            'remaining_tasks': remaining_by_date,
            'completed_tasks': completed_by_date
        })
    
    completion_rate = (completed_tasks / total_tasks) * 100
    
    return {
        'value': completion_rate,
        'data': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'remaining_tasks': remaining_tasks,
            'daily_progress': daily_progress
        }
    }


@shared_task
def generate_project_reports():
    """
    Gerar relatórios automáticos para projetos.
    """
    from apps.projects.models import Project
    from apps.dashboards.models import ProjectReport
    
    active_projects = Project.objects.filter(status='active')
    reports_generated = 0
    
    for project in active_projects:
        # Gerar relatório de saúde do projeto
        health_report = generate_project_health_report(project)
        
        if health_report:
            ProjectReport.objects.create(
                project=project,
                report_type='project_health',
                title=f'Relatório de Saúde - {project.name}',
                summary=health_report['summary'],
                data=health_report['data'],
                recommendations=health_report['recommendations'],
                period_start=timezone.now().date() - timedelta(days=7),
                period_end=timezone.now().date()
            )
            reports_generated += 1
    
    return f"Gerados {reports_generated} relatórios de projeto"


def generate_project_health_report(project):
    """
    Gerar relatório de saúde de um projeto específico.
    """
    from apps.tasks.models import Task
    
    # Métricas básicas
    total_tasks = project.tasks.count()
    completed_tasks = project.tasks.filter(status='done').count()
    overdue_tasks = project.tasks.filter(
        due_date__lt=timezone.now(),
        status__in=['todo', 'in_progress']
    ).count()
    
    if total_tasks == 0:
        return None
    
    # Calcular scores
    completion_score = (completed_tasks / total_tasks) * 100
    deadline_score = max(0, 100 - ((overdue_tasks / total_tasks) * 100))
    
    # Score geral (média dos scores)
    overall_score = (completion_score + deadline_score) / 2
    
    # Determinar status de saúde
    if overall_score >= 80:
        health_status = 'Excelente'
        health_color = 'green'
    elif overall_score >= 60:
        health_status = 'Boa'
        health_color = 'yellow'
    else:
        health_status = 'Atenção'
        health_color = 'red'
    
    # Gerar recomendações
    recommendations = []
    if overdue_tasks > 0:
        recommendations.append({
            'type': 'warning',
            'message': f'Há {overdue_tasks} tarefa(s) em atraso. Considere revisar prazos e prioridades.'
        })
    
    if completion_score < 50:
        recommendations.append({
            'type': 'info',
            'message': 'Progresso abaixo do esperado. Verifique se o time precisa de apoio adicional.'
        })
    
    summary = f"""
    Projeto: {project.name}
    Status de Saúde: {health_status} ({overall_score:.1f}/100)
    
    Métricas:
    - {completed_tasks}/{total_tasks} tarefas concluídas ({completion_score:.1f}%)
    - {overdue_tasks} tarefa(s) em atraso
    - Score de prazos: {deadline_score:.1f}%
    """
    
    return {
        'summary': summary.strip(),
        'data': {
            'overall_score': overall_score,
            'health_status': health_status,
            'health_color': health_color,
            'completion_score': completion_score,
            'deadline_score': deadline_score,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks
        },
        'recommendations': recommendations
    }


@shared_task
def calculate_team_workload():
    """
    Calcular carga de trabalho dos membros dos times.
    """
    from apps.teams.models import TeamMembership
    from apps.tasks.models import Task
    
    memberships = TeamMembership.objects.filter(is_active=True)
    workload_data = []
    
    for membership in memberships:
        # Tarefas ativas do usuário
        active_tasks = Task.objects.filter(
            assignee=membership.user,
            status__in=['todo', 'in_progress'],
            project__status='active'
        )
        
        total_hours = sum(task.estimated_hours or 0 for task in active_tasks)
        task_count = active_tasks.count()
        
        workload_data.append({
            'user_id': membership.user.id,
            'username': membership.user.username,
            'team_id': membership.team.id,
            'team_name': membership.team.name,
            'task_count': task_count,
            'estimated_hours': total_hours,
            'allocation_percentage': membership.allocation_percentage,
            'availability_hours': membership.user.availability_hours
        })
    
    # Salvar dados como snapshot
    from apps.dashboards.models import MetricSnapshot
    
    MetricSnapshot.objects.update_or_create(
        project=None,  # Métrica global
        metric_type='wip',
        period=f"{timezone.now().strftime('%Y-%m-%d')}",
        defaults={
            'value': len(workload_data),
            'data': {'team_workloads': workload_data}
        }
    )
    
    return f"Calculada carga de trabalho para {len(workload_data)} membros"