from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import DashboardWidget, MetricSnapshot, ProjectReport
from .serializers import DashboardWidgetSerializer, MetricSnapshotSerializer, ProjectReportSerializer
from apps.accounts.models import User
from apps.projects.models import Project
from apps.skills.models import UserSkill
from apps.tasks.models import Task


@extend_schema_view(
    list=extend_schema(tags=['MetricSnapshots'], summary='Listar metricas'),
    create=extend_schema(tags=['MetricSnapshots'], summary='Criar metrica'),
    retrieve=extend_schema(tags=['MetricSnapshots'], summary='Detalhes da metrica'),
    update=extend_schema(tags=['MetricSnapshots'], summary='Atualizar metrica'),
    destroy=extend_schema(tags=['MetricSnapshots'], summary='Excluir metrica'),
)
class MetricSnapshotViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar metricas.
    """
    queryset = MetricSnapshot.objects.all()
    serializer_class = MetricSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return MetricSnapshot.objects.all()
        return self.queryset


@extend_schema_view(
    list=extend_schema(tags=['ProjectReports'], summary='Listar relatorios'),
    create=extend_schema(tags=['ProjectReports'], summary='Criar relatorio'),
    retrieve=extend_schema(tags=['ProjectReports'], summary='Detalhes do relatorio'),
    update=extend_schema(tags=['ProjectReports'], summary='Atualizar relatorio'),
    destroy=extend_schema(tags=['ProjectReports'], summary='Excluir relatorio'),
)
class ProjectReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar relatorios.
    """
    queryset = ProjectReport.objects.all()
    serializer_class = ProjectReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return ProjectReport.objects.all()
        return self.queryset


@extend_schema_view(
    list=extend_schema(tags=['DashboardWidgets'], summary='Listar widgets'),
    create=extend_schema(tags=['DashboardWidgets'], summary='Criar widget'),
    retrieve=extend_schema(tags=['DashboardWidgets'], summary='Detalhes do widget'),
    update=extend_schema(tags=['DashboardWidgets'], summary='Atualizar widget'),
    destroy=extend_schema(tags=['DashboardWidgets'], summary='Excluir widget'),
)
class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar widgets.
    """
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return DashboardWidget.objects.all()
        return self.queryset


@login_required
def main_dashboard(request):
    """
    View principal do dashboard com métricas e estatísticas.
    """
    # Calculate comprehensive statistics
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status='active').count()
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='done').count()
    total_members = User.objects.filter(is_active=True).count()
    
    # Calculate overdue tasks
    today = timezone.now().date()
    overdue_tasks = Task.objects.filter(
        due_date__lt=today,
        status__in=['todo', 'in_progress']
    ).count()
    
    # Recent projects (last 5)
    recent_projects = Project.objects.all().order_by('-created_at')[:5]
    for project in recent_projects:
        # Add progress calculation
        project_tasks = Task.objects.filter(project=project)
        if project_tasks.exists():
            completed = project_tasks.filter(status='done').count()
            project.progress = int((completed / project_tasks.count()) * 100)
        else:
            project.progress = 0
    
    # Priority tasks (high priority, not completed)
    priority_tasks = Task.objects.filter(
        priority__gte=3,  # Alta (3) e Crítica (4)
        status__in=['todo', 'in_progress']
    ).order_by('due_date')[:5]
    
    # Mock recent activities (you can replace with actual activity tracking)
    recent_activities = [
        {
            'type': 'project_created',
            'user': request.user,
            'description': 'criou um novo projeto',
            'created_at': timezone.now() - timezone.timedelta(minutes=30)
        },
        {
            'type': 'task_completed',
            'user': request.user,
            'description': 'completou uma task importante',
            'created_at': timezone.now() - timezone.timedelta(hours=2)
        },
        {
            'type': 'user_joined',
            'user': request.user,
            'description': 'ingressou na equipe',
            'created_at': timezone.now() - timezone.timedelta(days=1)
        }
    ]
    
    project_status_breakdown = {
        label: Project.objects.filter(status=code).count()
        for code, label in Project.STATUS_CHOICES
    }
    skill_level_distribution = {
        str(level): UserSkill.objects.filter(level=level).count()
        for level, _ in UserSkill.LEVEL_CHOICES
    }

    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'total_members': total_members,
        'overdue_tasks': overdue_tasks,
        'recent_projects': recent_projects,
        'priority_tasks': priority_tasks,
        'recent_activities': recent_activities,
        'project_status_breakdown': project_status_breakdown,
        'skill_level_distribution': skill_level_distribution,
    }

    return render(request, 'dashboards/main.html', context)

