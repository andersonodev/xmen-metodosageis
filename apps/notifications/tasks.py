from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def daily_deadline_alerts():
    """
    Tarefa diária para enviar alertas de prazos próximos.
    """
    from apps.tasks.models import Task
    from apps.notifications.models import Notification
    
    # Tarefas que vencem em 24 horas
    tomorrow = timezone.now() + timedelta(days=1)
    upcoming_tasks = Task.objects.filter(
        due_date__lte=tomorrow,
        due_date__gte=timezone.now(),
        status__in=['todo', 'in_progress'],
        assignee__isnull=False
    )
    
    notifications_created = 0
    
    for task in upcoming_tasks:
        # Verificar se já existe notificação
        existing = Notification.objects.filter(
            user=task.assignee,
            type='task_due',
            content_type__model='task',
            object_id=task.id,
            created_at__date=timezone.now().date()
        ).exists()
        
        if not existing:
            Notification.objects.create(
                user=task.assignee,
                type='task_due',
                title=f'Prazo próximo: {task.title}',
                message=f'A tarefa "{task.title}" vence em breve ({task.due_date.strftime("%d/%m/%Y %H:%M")}).',
                priority='high',
                content_object=task,
                send_email=True
            )
            notifications_created += 1
    
    return f"Criadas {notifications_created} notificações de prazo"


@shared_task
def send_overdue_alerts():
    """
    Enviar alertas para tarefas em atraso.
    """
    from apps.tasks.models import Task
    from apps.notifications.models import Notification
    
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.now(),
        status__in=['todo', 'in_progress'],
        assignee__isnull=False
    )
    
    notifications_created = 0
    
    for task in overdue_tasks:
        # Verificar se já existe notificação hoje
        existing = Notification.objects.filter(
            user=task.assignee,
            type='task_due',
            content_type__model='task',
            object_id=task.id,
            created_at__date=timezone.now().date()
        ).exists()
        
        if not existing:
            days_overdue = (timezone.now().date() - task.due_date.date()).days
            
            Notification.objects.create(
                user=task.assignee,
                type='task_due',
                title=f'Tarefa em atraso: {task.title}',
                message=f'A tarefa "{task.title}" está {days_overdue} dia(s) em atraso.',
                priority='urgent',
                content_object=task,
                send_email=True
            )
            notifications_created += 1
    
    return f"Criadas {notifications_created} notificações de atraso"


@shared_task
def cleanup_old_notifications():
    """
    Limpar notificações antigas (mais de 30 dias).
    """
    from apps.notifications.models import Notification
    
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = Notification.objects.filter(
        created_at__lt=cutoff_date,
        is_read=True
    ).delete()[0]
    
    return f"Removidas {deleted_count} notificações antigas"


@shared_task
def process_email_notifications():
    """
    Processar fila de emails de notificações.
    """
    from apps.notifications.models import Notification
    from django.core.mail import send_mail
    from django.conf import settings
    
    # Buscar notificações pendentes de email
    pending_notifications = Notification.objects.filter(
        send_email=True,
        email_sent=False,
        created_at__gte=timezone.now() - timedelta(hours=1)  # Apenas últimas 1h
    )[:50]  # Limitar a 50 por vez
    
    emails_sent = 0
    
    for notification in pending_notifications:
        try:
            # Verificar preferências do usuário
            preferences = getattr(notification.user, 'notification_preferences', None)
            if preferences and preferences.email_frequency == 'never':
                notification.email_sent = True
                notification.save()
                continue
            
            # Enviar email
            send_mail(
                subject=f'[AgileTeam] {notification.title}',
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                fail_silently=False
            )
            
            notification.email_sent = True
            notification.save()
            emails_sent += 1
            
        except Exception as e:
            # Log do erro (em produção usar logging)
            continue
    
    return f"Enviados {emails_sent} emails de notificação"