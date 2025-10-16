from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from drf_spectacular.utils import extend_schema, extend_schema_view
from datetime import datetime, timedelta
import json

from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer


@extend_schema_view(
    list=extend_schema(tags=['Notifications'], summary='Listar notifications'),
    create=extend_schema(tags=['Notifications'], summary='Criar notification'),
    retrieve=extend_schema(tags=['Notifications'], summary='Detalhes do notification'),
    update=extend_schema(tags=['Notifications'], summary='Atualizar notification'),
    destroy=extend_schema(tags=['Notifications'], summary='Excluir notification'),
)
class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar notifications.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return Notification.objects.all()
        return self.queryset


@extend_schema_view(
    list=extend_schema(tags=['NotificationPreferences'], summary='Listar notificationpreferences'),
    create=extend_schema(tags=['NotificationPreferences'], summary='Criar notificationpreference'),
    retrieve=extend_schema(tags=['NotificationPreferences'], summary='Detalhes do notificationpreference'),
    update=extend_schema(tags=['NotificationPreferences'], summary='Atualizar notificationpreference'),
    destroy=extend_schema(tags=['NotificationPreferences'], summary='Excluir notificationpreference'),
)
class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar notificationpreferences.
    """
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return NotificationPreference.objects.all()
        return self.queryset


# Web Views

@login_required
def notification_list(request):
    """Listar notificações do usuário."""
    # Buscar notificações do usuário
    notifications_qs = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Aplicar filtros
    filter_type = request.GET.get('filter', 'all')
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    if filter_type == 'unread':
        notifications_qs = notifications_qs.filter(is_read=False)
    elif filter_type == 'read':
        notifications_qs = notifications_qs.filter(is_read=True)
    elif filter_type == 'today':
        notifications_qs = notifications_qs.filter(created_at__date=today)
    
    # Estatísticas
    all_notifications = Notification.objects.filter(user=request.user)
    stats = {
        'total_notifications': all_notifications.count(),
        'unread_count': all_notifications.filter(is_read=False).count(),
        'today_count': all_notifications.filter(created_at__date=today).count(),
        'week_count': all_notifications.filter(created_at__date__gte=week_start).count(),
    }
    
    context = {
        'notifications': notifications_qs[:50],  # Limitar a 50 por página
        'current_filter': filter_type,
        **stats,
    }
    return render(request, 'notifications/list.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def mark_as_read(request, pk):
    """Marcar notificação como lida."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    
    # Se for AJAX, retornar JSON
    if request.content_type == 'application/json':
        return JsonResponse({'success': True, 'message': 'Notificação marcada como lida'})
    
    return redirect('notifications:list')


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """Marcar todas as notificações como lidas."""
    try:
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False,
            is_active=True
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'{updated} notificações marcadas como lidas'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

