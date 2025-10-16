from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin para Notificações."""
    
    list_display = ['title', 'user', 'type', 'priority', 'is_read', 'send_email', 'email_sent', 'created_at']
    list_filter = ['type', 'priority', 'is_read', 'send_email', 'email_sent', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at', 'read_at']
    list_editable = ['is_read', 'send_email']
    
    fieldsets = (
        ('Notificação', {
            'fields': ('user', 'type', 'priority', 'title', 'message')
        }),
        ('Relacionamento', {
            'fields': ('content_type', 'object_id')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Email', {
            'fields': ('send_email', 'email_sent')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'send_email_notification']
    
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"{queryset.count()} notificações marcadas como lidas.")
    mark_as_read.short_description = "Marcar como lidas"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"{queryset.count()} notificações marcadas como não lidas.")
    mark_as_unread.short_description = "Marcar como não lidas"
    
    def send_email_notification(self, request, queryset):
        queryset.update(send_email=True)
        self.message_user(request, f"{queryset.count()} notificações marcadas para envio por email.")
    send_email_notification.short_description = "Enviar por email"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin para Preferências de Notificação."""
    
    list_display = ['user', 'email_frequency', 'task_assigned_email', 'task_due_email', 'team_invitation_email', 'updated_at']
    list_filter = ['email_frequency', 'task_assigned_email', 'task_due_email', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Preferências de Tarefas', {
            'fields': ('task_assigned_email', 'task_assigned_push', 'task_due_email', 'task_due_push')
        }),
        ('Preferências de Projetos', {
            'fields': ('project_update_email', 'project_update_push')
        }),
        ('Preferências de Times', {
            'fields': ('team_invitation_email', 'team_invitation_push')
        }),
        ('Configurações Gerais', {
            'fields': ('email_frequency',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
