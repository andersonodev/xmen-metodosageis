from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Project, Sprint, OKR, KeyResult
from .serializers import ProjectSerializer, SprintSerializer, OKRSerializer, KeyResultSerializer
from apps.accounts.models import User
from apps.tasks.models import Task


@extend_schema_view(
    list=extend_schema(tags=['Projects'], summary='Listar projetos'),
    create=extend_schema(tags=['Projects'], summary='Criar projeto'),
    retrieve=extend_schema(tags=['Projects'], summary='Detalhes do projeto'),
    update=extend_schema(tags=['Projects'], summary='Atualizar projeto'),
    destroy=extend_schema(tags=['Projects'], summary='Excluir projeto'),
)
class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar projetos.
    """
    queryset = Project.objects.exclude(status__in=['cancelled', 'completed'])
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(
            models.Q(team__memberships__user=self.request.user) |
            models.Q(created_by=self.request.user)
        ).exclude(status__in=['cancelled', 'completed']).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def sprints(self, request, pk=None):
        """Listar sprints do projeto"""
        project = self.get_object()
        sprints = project.sprints.all().order_by('-start_date')
        serializer = SprintSerializer(sprints, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def okrs(self, request, pk=None):
        """Listar OKRs do projeto"""
        project = self.get_object()
        okrs = project.okrs.all().order_by('-created_at')
        serializer = OKRSerializer(okrs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Arquivar projeto"""
        project = self.get_object()
        project.status = 'completed'
        project.save()
        return Response({'message': 'Projeto arquivado com sucesso'})


@extend_schema_view(
    list=extend_schema(tags=['Sprints'], summary='Listar sprints'),
    create=extend_schema(tags=['Sprints'], summary='Criar sprint'),
    retrieve=extend_schema(tags=['Sprints'], summary='Detalhes do sprint'),
    update=extend_schema(tags=['Sprints'], summary='Atualizar sprint'),
    destroy=extend_schema(tags=['Sprints'], summary='Excluir sprint'),
)
class SprintViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar sprints.
    """
    queryset = Sprint.objects.all()
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.request.query_params.get('project', None)
        if project_id:
            return self.queryset.filter(project_id=project_id)
        return self.queryset.filter(
            project__team__memberships__user=self.request.user
        ).distinct()

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Iniciar sprint"""
        sprint = self.get_object()
        sprint.status = 'active'
        sprint.start_date = timezone.now().date()
        sprint.save()
        return Response({'message': 'Sprint iniciado com sucesso'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Finalizar sprint"""
        sprint = self.get_object()
        sprint.status = 'completed'
        sprint.end_date = timezone.now().date()
        sprint.save()
        return Response({'message': 'Sprint finalizado com sucesso'})


@extend_schema_view(
    list=extend_schema(tags=['OKRs'], summary='Listar OKRs'),
    create=extend_schema(tags=['OKRs'], summary='Criar OKR'),
    retrieve=extend_schema(tags=['OKRs'], summary='Detalhes do OKR'),
    update=extend_schema(tags=['OKRs'], summary='Atualizar OKR'),
    destroy=extend_schema(tags=['OKRs'], summary='Excluir OKR'),
)
class OKRViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar OKRs.
    """
    queryset = OKR.objects.all()
    serializer_class = OKRSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.request.query_params.get('project', None)
        if project_id:
            return self.queryset.filter(project_id=project_id)
        return self.queryset.filter(
            project__team__memberships__user=self.request.user
        ).distinct()

    @action(detail=True, methods=['get'])
    def key_results(self, request, pk=None):
        """Listar Key Results do OKR"""
        okr = self.get_object()
        key_results = okr.key_results.all()
        serializer = KeyResultSerializer(key_results, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=['Key Results'], summary='Listar Key Results'),
    create=extend_schema(tags=['Key Results'], summary='Criar Key Result'),
    retrieve=extend_schema(tags=['Key Results'], summary='Detalhes do Key Result'),
    update=extend_schema(tags=['Key Results'], summary='Atualizar Key Result'),
    destroy=extend_schema(tags=['Key Results'], summary='Excluir Key Result'),
)
class KeyResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Key Results.
    """
    queryset = KeyResult.objects.all()
    serializer_class = KeyResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        okr_id = self.request.query_params.get('okr', None)
        if okr_id:
            return self.queryset.filter(okr_id=okr_id)
        return self.queryset.filter(
            okr__project__team__memberships__user=self.request.user
        ).distinct()

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Atualizar progresso do Key Result"""
        key_result = self.get_object()
        progress = request.data.get('progress', 0)
        
        if 0 <= progress <= 100:
            key_result.current_value = (key_result.target_value * progress) / 100
            key_result.save()
            return Response({'message': 'Progresso atualizado com sucesso'})
        else:
            return Response(
                {'error': 'Progresso deve estar entre 0 e 100'},
                status=status.HTTP_400_BAD_REQUEST
            )


# Web Views

@login_required
def project_list(request):
    """Listar todos os projetos."""
    projects = Project.objects.all().order_by('-created_at')
    
    # Calculate statistics
    total_projects = projects.count()
    active_projects = projects.filter(status='active').count()
    completed_projects = projects.filter(status='completed').count()
    delayed_projects = projects.filter(
        status='active',
        end_date__lt=timezone.now().date()
    ).count() if total_projects > 0 else 0
    
    # Add calculated fields to projects
    for project in projects:
        # Add team count
        if project.team:
            team_count = project.team.memberships.filter(is_active=True).count()
        else:
            team_count = 0
        
        # Add task count
        task_count = Task.objects.filter(project=project).count()
        
        # Add progress percentage
        total_tasks = Task.objects.filter(project=project).count()
        if total_tasks > 0:
            completed_tasks = Task.objects.filter(project=project, status='done').count()
            progress = int((completed_tasks / total_tasks) * 100)
        else:
            progress = 0
        
        # Store in a dictionary to pass to template
        project.stats = {
            'team_count': team_count,
            'task_count': task_count,
            'progress': progress
        }
    
    # Filtrar por status se especificado
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        projects = projects.filter(status=status_filter)
    
    context = {
        'projects': projects,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'delayed_projects': delayed_projects,
        'status_filter': status_filter or 'all',
    }
    return render(request, 'projects/list.html', context)


@login_required  
def project_detail(request, pk):
    """Detalhes de um projeto específico."""
    project = get_object_or_404(Project, pk=pk)
    
    # Buscar tarefas do projeto
    project_tasks = Task.objects.filter(project=project).order_by('-created_at')[:10]
    
    context = {
        'project': project,
        'project_tasks': project_tasks,
    }
    return render(request, 'projects/detail.html', context)


@login_required
def project_create(request):
    """Criar um novo projeto."""
    if request.method == 'POST':
        # Processar dados do formulário
        name = request.POST.get('name')
        description = request.POST.get('description')
        status_value = request.POST.get('status', 'active')
        priority = request.POST.get('priority', 'medium')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if name:
            project = Project.objects.create(
                name=name,
                description=description,
                status=status_value,
                priority=priority,
                start_date=start_date if start_date else None,
                end_date=end_date if end_date else None,
                created_by=request.user
            )
            
            # Adicionar membros da equipe
            team_members = request.POST.get('team_members')
            if team_members:
                member_ids = [int(id) for id in team_members.split(',') if id.isdigit()]
                members = User.objects.filter(id__in=member_ids)
                project.team_members.set(members)
            
            messages.success(request, 'Projeto criado com sucesso!')
            return redirect('projects:detail', pk=project.pk)
        else:
            messages.error(request, 'Nome do projeto é obrigatório.')
    
    return render(request, 'projects/create.html')


@login_required
def project_edit(request, pk):
    """Editar um projeto existente."""
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        # Atualizar dados do projeto
        project.name = request.POST.get('name', project.name)
        project.description = request.POST.get('description', project.description)
        project.status = request.POST.get('status', project.status)
        project.priority = request.POST.get('priority', project.priority)
        
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if start_date:
            project.start_date = start_date
        if end_date:
            project.end_date = end_date
            
        project.save()
        
        # Atualizar membros da equipe
        team_members = request.POST.get('team_members')
        if team_members:
            member_ids = [int(id) for id in team_members.split(',') if id.isdigit()]
            members = User.objects.filter(id__in=member_ids)
            project.team_members.set(members)
        
        messages.success(request, 'Projeto atualizado com sucesso!')
        return redirect('projects:detail', pk=project.pk)
    
    # Criar objeto form fictício para o template
    form = type('Form', (), {
        'name': type('Field', (), {'value': project.name}),
        'description': type('Field', (), {'value': project.description}),
        'status': type('Field', (), {'value': project.status}),
        'priority': type('Field', (), {'value': project.priority}),
        'start_date': type('Field', (), {'value': project.start_date}),
        'end_date': type('Field', (), {'value': project.end_date}),
    })
    
    context = {
        'project': project,
        'form': form,
    }
    return render(request, 'projects/create.html', context)
