from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey


class Notification(models.Model):
    """
    Sistema de notificações para usuários.
    """
    TYPE_CHOICES = [
        ('task_assigned', 'Tarefa Atribuída'),
        ('task_due', 'Prazo da Tarefa'),
        ('project_update', 'Atualização do Projeto'),
        ('team_invitation', 'Convite para Time'),
        ('sprint_started', 'Sprint Iniciado'),
        ('sprint_ended', 'Sprint Finalizado'),
        ('mention', 'Mencionado'),
        ('system', 'Sistema'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    # Destinatário
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Conteúdo
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Relacionamento genérico (tarefa, projeto, etc.)
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Estado
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Configurações de entrega
    send_email = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class NotificationPreference(models.Model):
    """
    Preferências de notificação do usuário.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Preferências por tipo
    task_assigned_email = models.BooleanField(default=True)
    task_assigned_push = models.BooleanField(default=True)
    
    task_due_email = models.BooleanField(default=True)
    task_due_push = models.BooleanField(default=True)
    
    project_update_email = models.BooleanField(default=False)
    project_update_push = models.BooleanField(default=True)
    
    team_invitation_email = models.BooleanField(default=True)
    team_invitation_push = models.BooleanField(default=True)
    
    # Configurações gerais
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Imediato'),
            ('daily', 'Diário'),
            ('weekly', 'Semanal'),
            ('never', 'Nunca'),
        ],
        default='immediate'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Preferência de Notificação'
        verbose_name_plural = 'Preferências de Notificações'
    
    def __str__(self):
        return f"Preferências de {self.user.username}"
