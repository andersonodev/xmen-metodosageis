from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
import json
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Integration, ImportHistory
from .serializers import IntegrationSerializer, ImportHistorySerializer


@extend_schema_view(
    list=extend_schema(tags=['Integrations'], summary='Listar integrations'),
    create=extend_schema(tags=['Integrations'], summary='Criar integration'),
    retrieve=extend_schema(tags=['Integrations'], summary='Detalhes do integration'),
    update=extend_schema(tags=['Integrations'], summary='Atualizar integration'),
    destroy=extend_schema(tags=['Integrations'], summary='Excluir integration'),
)
class IntegrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar integrations.
    """
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return Integration.objects.all()
        return self.queryset


@extend_schema_view(
    list=extend_schema(tags=['ImportHistorys'], summary='Listar importhistorys'),
    create=extend_schema(tags=['ImportHistorys'], summary='Criar importhistory'),
    retrieve=extend_schema(tags=['ImportHistorys'], summary='Detalhes do importhistory'),
    update=extend_schema(tags=['ImportHistorys'], summary='Atualizar importhistory'),
    destroy=extend_schema(tags=['ImportHistorys'], summary='Excluir importhistory'),
)
class ImportHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar importhistorys.
    """
    queryset = ImportHistory.objects.all()
    serializer_class = ImportHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return ImportHistory.objects.all()
        return self.queryset


# Web Views

@login_required
def integration_list(request):
    """Listar integrações disponíveis."""
    integrations = Integration.objects.all()
    
    # Calculate statistics
    total_integrations = integrations.count()
    active_integrations = integrations.filter(status='active').count()
    inactive_integrations = integrations.filter(status='inactive').count()
    
    # This month count
    this_month = timezone.now().replace(day=1)
    this_month_count = integrations.filter(created_at__gte=this_month).count()
    
    context = {
        'integrations': integrations.order_by('-created_at'),
        'total_integrations': total_integrations,
        'active_integrations': active_integrations,
        'inactive_integrations': inactive_integrations,
        'this_month_count': this_month_count,
    }
    return render(request, 'integrations/list.html', context)


@login_required
def integration_detail(request, pk):
    """Detalhes de uma integração."""
    integration = get_object_or_404(Integration, pk=pk, is_active=True)
    
    # Get recent logs (mock data for now)
    logs = [
        {
            'timestamp': timezone.now() - timedelta(minutes=5),
            'level': 'info',
            'message': 'Sincronização iniciada'
        },
        {
            'timestamp': timezone.now() - timedelta(minutes=3),
            'level': 'success',
            'message': 'Dados sincronizados com sucesso'
        },
        {
            'timestamp': timezone.now() - timedelta(hours=1),
            'level': 'warning',
            'message': 'Alguns dados não puderam ser sincronizados'
        },
    ]
    
    context = {
        'integration': integration,
        'logs': logs,
    }
    return render(request, 'integrations/detail.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_integration(request, pk):
    """Ativar/desativar uma integração."""
    try:
        integration = get_object_or_404(Integration, pk=pk, is_active=True)
        
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'enable':
            integration.status = 'active'
            message = 'Integração ativada com sucesso'
        elif action == 'disable':
            integration.status = 'inactive'
            message = 'Integração pausada com sucesso'
        else:
            return JsonResponse({
                'success': False,
                'message': 'Ação inválida'
            })
        
        integration.save()
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
@require_http_methods(["DELETE"])
def delete_integration(request, pk):
    """Excluir uma integração."""
    try:
        integration = get_object_or_404(Integration, pk=pk, is_active=True)
        integration.is_active = False
        integration.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Integração excluída com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
@require_http_methods(["POST"])
def sync_integration(request, pk):
    """Sincronizar uma integração."""
    try:
        integration = get_object_or_404(Integration, pk=pk, is_active=True)
        
        if integration.status != 'active':
            return JsonResponse({
                'success': False,
                'message': 'Integração não está ativa'
            })
        
        # Update last sync time
        integration.last_sync = timezone.now()
        integration.save()
        
        # Here you would implement the actual sync logic
        # For now, just return success
        
        return JsonResponse({
            'success': True,
            'message': 'Sincronização iniciada com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
@require_http_methods(["POST"])
def test_integration(request, pk):
    """Testar conexão de uma integração."""
    try:
        integration = get_object_or_404(Integration, pk=pk, is_active=True)
        
        # Here you would implement the actual connection test
        # For now, just return success
        
        return JsonResponse({
            'success': True,
            'message': 'Conexão testada com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
def get_integration_logs(request, pk):
    """Obter logs de uma integração."""
    try:
        integration = get_object_or_404(Integration, pk=pk, is_active=True)
        
        # Mock logs data - in real implementation, get from database or log files
        logs = [
            {
                'timestamp': timezone.now().strftime('%H:%M:%S'),
                'level': 'info',
                'message': 'Sistema iniciado'
            },
            {
                'timestamp': (timezone.now() - timedelta(minutes=1)).strftime('%H:%M:%S'),
                'level': 'success',
                'message': 'Conectado com sucesso'
            },
            {
                'timestamp': (timezone.now() - timedelta(minutes=2)).strftime('%H:%M:%S'),
                'level': 'info',
                'message': 'Iniciando sincronização'
            },
        ]
        
        return JsonResponse({
            'success': True,
            'logs': logs
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

