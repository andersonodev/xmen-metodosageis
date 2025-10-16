from django.contrib import admin
from .models import Column, Task, TaskComment, TaskAttachment, TaskHistory


class TaskCommentInline(admin.TabularInline):
    """Inline para comentários da tarefa."""
    model = TaskComment
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['author', 'content', 'created_at']


class TaskAttachmentInline(admin.TabularInline):
    """Inline para anexos da tarefa."""
    model = TaskAttachment
    extra = 0
    readonly_fields = ['uploaded_at', 'size_mb']
    fields = ['name', 'file', 'size_mb', 'uploaded_by', 'uploaded_at']


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    """Admin para Colunas do Kanban."""
    
    list_display = ['name', 'project', 'position', 'task_count', 'wip_limit', 'is_done_column']
    list_filter = ['project', 'is_done_column', 'created_at']
    search_fields = ['name', 'project__name']
    readonly_fields = ['created_at', 'task_count']
    list_editable = ['position', 'wip_limit', 'is_done_column']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('project', 'name', 'position')
        }),
        ('Configurações', {
            'fields': ('color', 'wip_limit', 'is_done_column')
        }),
        ('Estatísticas', {
            'fields': ('task_count',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def task_count(self, obj):
        return obj.task_count
    task_count.short_description = 'Qtd Tarefas'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin para Tarefas."""
    
    list_display = ['title', 'project', 'type', 'status', 'priority', 'assignee', 'story_points', 'created_at']
    list_filter = ['type', 'status', 'priority', 'project', 'column', 'assignee', 'created_at']
    search_fields = ['title', 'description', 'project__name', 'assignee__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status', 'priority', 'assignee']
    inlines = [TaskCommentInline, TaskAttachmentInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'description', 'type', 'priority')
        }),
        ('Relacionamentos', {
            'fields': ('project', 'column', 'assignee', 'sprint')
        }),
        ('Status e Posição', {
            'fields': ('status', 'position')
        }),
        ('Estimativas', {
            'fields': ('story_points', 'estimated_hours', 'actual_hours')
        }),
        ('Datas', {
            'fields': ('due_date', 'started_at', 'completed_at')
        }),
        ('Metadados', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    """Admin para Comentários de Tarefas."""
    
    list_display = ['task', 'author', 'content_preview', 'created_at', 'updated_at']
    list_filter = ['task__project', 'author', 'created_at']
    search_fields = ['content', 'task__title', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Comentário', {
            'fields': ('task', 'author', 'content')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Conteúdo'


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    """Admin para Anexos de Tarefas."""
    
    list_display = ['name', 'task', 'size_mb', 'uploaded_by', 'uploaded_at']
    list_filter = ['task__project', 'uploaded_by', 'uploaded_at']
    search_fields = ['name', 'task__title', 'uploaded_by__username']
    readonly_fields = ['size', 'uploaded_at', 'size_mb']
    
    fieldsets = (
        ('Anexo', {
            'fields': ('task', 'name', 'file')
        }),
        ('Metadados', {
            'fields': ('size', 'size_mb', 'uploaded_by', 'uploaded_at'),
            'classes': ('collapse',)
        }),
    )
    
    def size_mb(self, obj):
        return f"{obj.size_mb} MB"
    size_mb.short_description = 'Tamanho'


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    """Admin para Histórico de Tarefas."""
    
    list_display = ['task', 'user', 'action', 'created_at']
    list_filter = ['action', 'task__project', 'user', 'created_at']
    search_fields = ['task__title', 'user__username']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Histórico', {
            'fields': ('task', 'user', 'action', 'details')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
