from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
import json

from .models import Task, Column, TaskComment
from .serializers import TaskSerializer, ColumnSerializer, TaskCommentSerializer

User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=['Tasks'], summary='Listar tasks'),
    create=extend_schema(tags=['Tasks'], summary='Criar task'),
    retrieve=extend_schema(tags=['Tasks'], summary='Detalhes do task'),
    update=extend_schema(tags=['Tasks'], summary='Atualizar task'),
    destroy=extend_schema(tags=['Tasks'], summary='Excluir task'),
)
class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar tasks.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return Task.objects.all()
        return self.queryset


@extend_schema_view(
    list=extend_schema(tags=['Columns'], summary='Listar columns'),
    create=extend_schema(tags=['Columns'], summary='Criar column'),
    retrieve=extend_schema(tags=['Columns'], summary='Detalhes do column'),
    update=extend_schema(tags=['Columns'], summary='Atualizar column'),
    destroy=extend_schema(tags=['Columns'], summary='Excluir column'),
)
class ColumnViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar columns.
    """
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return Column.objects.all()
        return self.queryset


@extend_schema_view(
    list=extend_schema(tags=['TaskComments'], summary='Listar taskcomments'),
    create=extend_schema(tags=['TaskComments'], summary='Criar taskcomment'),
    retrieve=extend_schema(tags=['TaskComments'], summary='Detalhes do taskcomment'),
    update=extend_schema(tags=['TaskComments'], summary='Atualizar taskcomment'),
    destroy=extend_schema(tags=['TaskComments'], summary='Excluir taskcomment'),
)
class TaskCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar taskcomments.
    """
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return TaskComment.objects.all()
        return self.queryset


# Web Views

@login_required
def task_board(request, project_id=None):
    """Kanban board para visualizar e gerenciar tarefas."""
    # Buscar projeto se especificado
    project = None
    if project_id:
        from apps.projects.models import Project
        project = get_object_or_404(Project, pk=project_id)
    
    # Buscar colunas padrão ou criar se não existirem
    columns = Column.objects.all().order_by('position')
    if not columns.exists():
        # Criar colunas padrão
        default_columns = [
            ('Backlog', 0, '#6c757d'),
            ('To Do', 1, '#007bff'),
            ('In Progress', 2, '#ffc107'),
            ('Review', 3, '#17a2b8'),
            ('Done', 4, '#28a745'),
        ]
        for name, position, color in default_columns:
            Column.objects.create(name=name, position=position, color=color, project=project)
        columns = Column.objects.all().order_by('position')
    
    # Buscar tarefas
    tasks = Task.objects.select_related(
        'assignee', 
        'project', 
        'project__team',
        'column'
    ).prefetch_related(
        'comments',
        'project__team__memberships__user'
    )
    if project:
        tasks = tasks.filter(project=project)
    
    # Organizar tarefas por coluna
    task_columns = {}
    for column in columns:
        column_tasks = tasks.filter(column=column).order_by('position', '-priority')
        task_columns[column] = column_tasks
    
    # Buscar usuários para atribuição
    users = User.objects.filter(is_active=True).order_by('first_name', 'username')
    
    # Buscar projetos para filtro
    from apps.projects.models import Project
    projects = Project.objects.filter(status='active').order_by('name')
    
    context = {
        'project': project,
        'projects': projects,
        'columns': columns,
        'task_columns': task_columns,
        'total_tasks': tasks.count(),
        'users': users,
    }
    return render(request, 'tasks/board.html', context)


@login_required
def task_detail(request, pk):
    """Detalhes de uma tarefa específica."""
    task = get_object_or_404(Task, pk=pk)
    comments = TaskComment.objects.filter(task=task).order_by('-created_at')
    
    context = {
        'task': task,
        'comments': comments,
    }
    return render(request, 'tasks/detail.html', context)


@login_required
def task_create(request, project_id=None):
    """Criar uma nova tarefa."""
    project = None
    if project_id:
        from apps.projects.models import Project
        project = get_object_or_404(Project, pk=project_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'medium')
        column_id = request.POST.get('column')
        assigned_to_id = request.POST.get('assigned_to')
        
        if title:
            # Buscar primeira coluna como padrão
            column = None
            if column_id:
                column = Column.objects.filter(pk=column_id).first()
            if not column:
                column = Column.objects.all().order_by('position').first()
            
            # Buscar usuário atribuído
            assigned_to = None
            if assigned_to_id:
                assigned_to = User.objects.filter(pk=assigned_to_id).first()
            
            task = Task.objects.create(
                title=title,
                description=description,
                priority=priority,
                column=column,
                project=project,
                assignee=assigned_to,
                created_by=request.user
            )
            
            messages.success(request, 'Tarefa criada com sucesso!')
            
            if project:
                return redirect('tasks:board', project_id=project.pk)
            else:
                return redirect('tasks:board')
        else:
            messages.error(request, 'Título da tarefa é obrigatório.')
    
    # Buscar dados para o formulário
    columns = Column.objects.all().order_by('position')
    users = User.objects.filter(is_active=True)
    
    context = {
        'project': project,
        'columns': columns,
        'users': users,
    }
    return render(request, 'tasks/create.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_task_column(request):
    """Atualizar a coluna de uma tarefa via AJAX."""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        column_id = data.get('column_id')
        
        task = get_object_or_404(Task, pk=task_id)
        column = get_object_or_404(Column, pk=column_id)
        
        task.column = column
        task.save()
        
        return JsonResponse({'success': True, 'message': 'Tarefa movida com sucesso!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_column(request):
    """Criar uma nova coluna via AJAX."""
    try:
        data = json.loads(request.body)
        name = data.get('name')
        color = data.get('color', '#6B73FF')
        project_id = data.get('project_id')
        
        if not name:
            return JsonResponse({'success': False, 'message': 'Nome da coluna é obrigatório'}, status=400)
        
        # Buscar próxima posição
        max_position = Column.objects.aggregate(models.Max('position'))['position__max'] or 0
        
        project = None
        if project_id:
            from apps.projects.models import Project
            project = get_object_or_404(Project, pk=project_id)
        
        column = Column.objects.create(
            name=name,
            color=color,
            position=max_position + 1,
            project=project
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Coluna criada com sucesso!',
            'column': {
                'id': column.id,
                'name': column.name,
                'color': column.color,
                'position': column.position
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_column(request, column_id):
    """Atualizar uma coluna via AJAX."""
    try:
        data = json.loads(request.body)
        column = get_object_or_404(Column, pk=column_id)
        
        if 'name' in data:
            column.name = data['name']
        if 'color' in data:
            column.color = data['color']
        if 'wip_limit' in data:
            column.wip_limit = data['wip_limit'] if data['wip_limit'] else None
        
        column.save()
        
        return JsonResponse({'success': True, 'message': 'Coluna atualizada com sucesso!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_column(request, column_id):
    """Deletar uma coluna via AJAX."""
    try:
        column = get_object_or_404(Column, pk=column_id)
        
        # Verificar se há tarefas na coluna
        if column.tasks.exists():
            return JsonResponse({
                'success': False, 
                'message': 'Não é possível deletar uma coluna que contém tarefas'
            }, status=400)
        
        column.delete()
        
        return JsonResponse({'success': True, 'message': 'Coluna deletada com sucesso!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_task_quick(request):
    """Criar uma nova tarefa rapidamente via AJAX."""
    try:
        data = json.loads(request.body)
        title = data.get('title')
        column_id = data.get('column_id')
        project_id = data.get('project_id')
        task_type = data.get('type', 'task')
        priority = data.get('priority', 2)
        assignee_id = data.get('assignee_id')
        description = data.get('description', '')
        
        if not title:
            return JsonResponse({'success': False, 'message': 'Título é obrigatório'}, status=400)
        
        column = get_object_or_404(Column, pk=column_id)
        
        project = None
        if project_id:
            from apps.projects.models import Project
            project = get_object_or_404(Project, pk=project_id)
        
        assignee = None
        if assignee_id:
            assignee = User.objects.filter(pk=assignee_id).first()
        
        task = Task.objects.create(
            title=title,
            description=description,
            type=task_type,
            priority=priority,
            column=column,
            project=project,
            assignee=assignee,
            created_by=request.user,
            status='todo'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Tarefa criada com sucesso!',
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'type': task.type,
                'priority': task.priority,
                'assignee': task.assignee.username if task.assignee else None,
                'assignee_name': task.assignee.get_full_name() if task.assignee else None,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
def task_detail_modal(request, pk):
    """Retornar dados da tarefa para modal via AJAX."""
    try:
        task = get_object_or_404(Task, pk=pk)
        comments = TaskComment.objects.filter(task=task).select_related('author').order_by('-created_at')
        users = User.objects.filter(is_active=True).order_by('first_name', 'username')
        columns = Column.objects.all().order_by('position')
        
        from apps.projects.models import Project
        projects = Project.objects.filter(status='active').order_by('name')
        
        # Buscar role do assignee na equipe se existir
        assignee_role = None
        if task.assignee and task.project and task.project.team:
            from apps.teams.models import TeamMembership
            try:
                membership = TeamMembership.objects.get(
                    user=task.assignee, 
                    team=task.project.team, 
                    is_active=True
                )
                assignee_role = membership.get_role_display()
            except TeamMembership.DoesNotExist:
                pass

        task_data = {
            'id': task.id,
            'title': task.title,
            'description': task.description or '',
            'type': task.type,
            'priority': task.priority,
            'status': task.status,
            'story_points': task.story_points,
            'estimated_hours': task.estimated_hours,
            'actual_hours': task.actual_hours,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'assignee_id': task.assignee.id if task.assignee else None,
            'assignee_name': task.assignee.get_full_name() if task.assignee else None,
            'assignee_role': assignee_role,
            'project_id': task.project.id if task.project else None,
            'project_name': task.project.name if task.project else None,
            'column_id': task.column.id,
            'column_name': task.column.name,
            'created_by': task.created_by.get_full_name() or task.created_by.username,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat(),
            'is_overdue': task.is_overdue,
        }
        
        comments_data = [{
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.get_full_name() or comment.author.username,
            'author_id': comment.author.id,
            'created_at': comment.created_at.isoformat(),
        } for comment in comments]
        
        users_data = []
        for user in users:
            # Buscar role do usuário na equipe se o projeto tiver equipe
            role = None
            if task.project and task.project.team:
                from apps.teams.models import TeamMembership
                try:
                    membership = TeamMembership.objects.get(
                        user=user, 
                        team=task.project.team, 
                        is_active=True
                    )
                    role = membership.get_role_display()
                except TeamMembership.DoesNotExist:
                    pass
            
            users_data.append({
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'username': user.username,
                'role': role,
            })
        
        columns_data = [{
            'id': column.id,
            'name': column.name,
            'color': column.color,
        } for column in columns]
        
        projects_data = [{
            'id': project.id,
            'name': project.name,
        } for project in projects]
        
        return JsonResponse({
            'success': True,
            'task': task_data,
            'comments': comments_data,
            'users': users_data,
            'columns': columns_data,
            'projects': projects_data,
            'type_choices': Task.TYPE_CHOICES,
            'priority_choices': Task.PRIORITY_CHOICES,
            'status_choices': Task.STATUS_CHOICES,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_task(request, pk):
    """Atualizar uma tarefa via AJAX."""
    try:
        data = json.loads(request.body)
        task = get_object_or_404(Task, pk=pk)
        
        # Atualizar campos se fornecidos
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'type' in data:
            task.type = data['type']
        if 'priority' in data:
            task.priority = data['priority']
        if 'status' in data:
            task.status = data['status']
        if 'story_points' in data:
            task.story_points = data['story_points'] if data['story_points'] else None
        if 'estimated_hours' in data:
            task.estimated_hours = data['estimated_hours'] if data['estimated_hours'] else None
        if 'actual_hours' in data:
            task.actual_hours = data['actual_hours'] or 0
        if 'due_date' in data:
            if data['due_date']:
                from django.utils.dateparse import parse_datetime
                task.due_date = parse_datetime(data['due_date'])
            else:
                task.due_date = None
        if 'assignee_id' in data:
            if data['assignee_id']:
                task.assignee = get_object_or_404(User, pk=data['assignee_id'])
            else:
                task.assignee = None
        if 'project_id' in data:
            if data['project_id']:
                from apps.projects.models import Project
                task.project = get_object_or_404(Project, pk=data['project_id'])
        if 'column_id' in data:
            task.column = get_object_or_404(Column, pk=data['column_id'])
        
        task.save()
        
        return JsonResponse({'success': True, 'message': 'Tarefa atualizada com sucesso!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_comment(request, task_id):
    """Adicionar comentário a uma tarefa via AJAX."""
    try:
        data = json.loads(request.body)
        content = data.get('content')
        
        if not content:
            return JsonResponse({'success': False, 'message': 'Conteúdo do comentário é obrigatório'}, status=400)
        
        task = get_object_or_404(Task, pk=task_id)
        
        comment = TaskComment.objects.create(
            task=task,
            author=request.user,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Comentário adicionado com sucesso!',
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author': comment.author.get_full_name() or comment.author.username,
                'author_id': comment.author.id,
                'created_at': comment.created_at.isoformat(),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_task(request, pk):
    """Deletar uma tarefa via AJAX."""
    try:
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        
        return JsonResponse({'success': True, 'message': 'Tarefa deletada com sucesso!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
def task_list(request):
    """Listar todas as tarefas em formato de lista."""
    tasks = Task.objects.all().select_related(
        'project', 
        'project__team',
        'assignee', 
        'column'
    ).prefetch_related(
        'project__team__memberships__user'
    ).order_by('-created_at')
    
    # Calculate statistics
    total_tasks = tasks.count()
    todo_tasks = tasks.filter(status='todo').count()
    progress_tasks = tasks.filter(status='in_progress').count()
    completed_tasks = tasks.filter(status='done').count()
    
    # Get today's date for comparisons
    today = timezone.now().date()
    
    # Add additional context to tasks
    for task in tasks:
        # Check if task is overdue
        if task.due_date and task.due_date < today and task.status != 'done':
            task.is_overdue = True
        else:
            task.is_overdue = False
            
        # Check if due today
        if task.due_date == today:
            task.is_due_today = True
        else:
            task.is_due_today = False
    
    # Filtros
    project_filter = request.GET.get('project')
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    assigned_filter = request.GET.get('assigned')
    
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if assigned_filter:
        tasks = tasks.filter(assigned_to_id=assigned_filter)
    
    # Buscar dados para filtros
    from apps.projects.models import Project
    
    projects = Project.objects.filter(status='active')
    users = User.objects.filter(is_active=True)
    columns = Column.objects.all()
    
    context = {
        'tasks': tasks,
        'projects': projects,
        'users': users,
        'columns': columns,
        'total_tasks': total_tasks,
        'todo_tasks': todo_tasks,
        'progress_tasks': progress_tasks,
        'completed_tasks': completed_tasks,
        'today': today,
        'filters': {
            'project': project_filter,
            'status': status_filter,
            'priority': priority_filter,
            'assigned': assigned_filter,
        }
    }
    return render(request, 'tasks/list.html', context)

