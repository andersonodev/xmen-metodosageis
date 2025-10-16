from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Column(models.Model):
    """
    Coluna do quadro Kanban.
    """
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='columns',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField()
    color = models.CharField(max_length=7, default='#6B73FF')  # Hex color
    
    # Configurações da coluna
    wip_limit = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Work In Progress limit"
    )
    is_done_column = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task_columns'
        verbose_name = 'Coluna'
        verbose_name_plural = 'Colunas'
        ordering = ['project', 'position']
    
    def __str__(self):
        if self.project:
            return f"{self.project.name} - {self.name}"
        return self.name
    
    @property
    def task_count(self):
        return self.tasks.count()
    
    @property
    def is_over_wip_limit(self):
        if not self.wip_limit:
            return False
        return self.task_count > self.wip_limit


class Task(models.Model):
    """
    Tarefa no quadro Kanban.
    """
    PRIORITY_CHOICES = [
        (1, 'Baixa'),
        (2, 'Normal'),
        (3, 'Alta'),
        (4, 'Crítica'),
    ]
    
    TYPE_CHOICES = [
        ('story', 'User Story'),
        ('bug', 'Bug'),
        ('task', 'Tarefa'),
        ('epic', 'Epic'),
        ('spike', 'Spike'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'Em Progresso'),
        ('review', 'Em Revisão'),
        ('done', 'Concluído'),
    ]
    
    # Informações básicas
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='task')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    
    # Relacionamentos
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )
    column = models.ForeignKey(
        Column,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    sprint = models.ForeignKey(
        'projects.Sprint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    
    # Estimativas e progresso
    story_points = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    actual_hours = models.PositiveIntegerField(default=0)
    
    # Posicionamento no board
    position = models.PositiveIntegerField(default=0)
    
    # Datas
    due_date = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadados
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['column__position', 'position', '-priority']
    
    def __str__(self):
        if self.project:
            return f"[{self.project.name}] {self.title}"
        return self.title
    
    @property
    def is_overdue(self):
        if not self.due_date or self.status == 'done':
            return False
        from django.utils import timezone
        return timezone.now() > self.due_date


class TaskComment(models.Model):
    """
    Comentário em uma tarefa.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'task_comments'
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comentário de {self.author.username} em {self.task.title}"


class TaskAttachment(models.Model):
    """
    Anexo de uma tarefa.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='task_attachments/')
    name = models.CharField(max_length=255)
    size = models.PositiveIntegerField()  # em bytes
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task_attachments'
        verbose_name = 'Anexo'
        verbose_name_plural = 'Anexos'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} - {self.task.title}"
    
    @property
    def size_mb(self):
        return round(self.size / 1024 / 1024, 2)


class TaskHistory(models.Model):
    """
    Histórico de mudanças em tarefas.
    """
    ACTION_CHOICES = [
        ('created', 'Criada'),
        ('updated', 'Atualizada'),
        ('moved', 'Movida'),
        ('assigned', 'Atribuída'),
        ('commented', 'Comentada'),
        ('completed', 'Concluída'),
    ]
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='history'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task_history'
        verbose_name = 'Histórico da Tarefa'
        verbose_name_plural = 'Histórico das Tarefas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task.title} - {self.get_action_display()}"
