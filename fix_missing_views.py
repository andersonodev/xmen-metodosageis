#!/usr/bin/env python3
"""
Script para criar views faltantes em todos os apps
"""
import os
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xmen_agileteam.settings')
django.setup()

def create_missing_views():
    """Cria views faltantes para todos os apps"""
    
    apps_to_fix = [
        {
            'app': 'tasks',
            'models': ['Task', 'Column', 'TaskComment'],
            'imports': 'from .models import Task, Column, TaskComment\nfrom .serializers import TaskSerializer, ColumnSerializer, TaskCommentSerializer'
        },
        {
            'app': 'dashboards', 
            'models': ['Dashboard', 'Widget', 'Metric'],
            'imports': 'from .models import Dashboard, Widget, Metric\nfrom .serializers import DashboardSerializer, WidgetSerializer, MetricSerializer'
        },
        {
            'app': 'notifications',
            'models': ['Notification', 'NotificationPreference'],
            'imports': 'from .models import Notification, NotificationPreference\nfrom .serializers import NotificationSerializer, NotificationPreferenceSerializer'
        },
        {
            'app': 'chat',
            'models': ['ChatRoom', 'Message'],
            'imports': 'from .models import ChatRoom, Message\nfrom .serializers import ChatRoomSerializer, MessageSerializer'
        },
        {
            'app': 'recommendations',
            'models': ['Recommendation'],
            'imports': 'from .models import Recommendation\nfrom .serializers import RecommendationSerializer'
        },
        {
            'app': 'integrations',
            'models': ['Integration', 'ImportLog'],
            'imports': 'from .models import Integration, ImportLog\nfrom .serializers import IntegrationSerializer, ImportLogSerializer'
        }
    ]
    
    for app_info in apps_to_fix:
        app_name = app_info['app']
        models = app_info['models']
        imports = app_info['imports']
        
        views_file = f"apps/{app_name}/views.py"
        
        # Template base para views
        content = f"""from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from drf_spectacular.utils import extend_schema, extend_schema_view

{imports}

"""
        
        for model in models:
            viewset_name = f"{model}ViewSet"
            serializer_name = f"{model}Serializer"
            
            content += f"""
@extend_schema_view(
    list=extend_schema(tags=['{model}s'], summary='Listar {model.lower()}s'),
    create=extend_schema(tags=['{model}s'], summary='Criar {model.lower()}'),
    retrieve=extend_schema(tags=['{model}s'], summary='Detalhes do {model.lower()}'),
    update=extend_schema(tags=['{model}s'], summary='Atualizar {model.lower()}'),
    destroy=extend_schema(tags=['{model}s'], summary='Excluir {model.lower()}'),
)
class {viewset_name}(viewsets.ModelViewSet):
    \"\"\"
    ViewSet para gerenciar {model.lower()}s.
    \"\"\"
    queryset = {model}.objects.all()
    serializer_class = {serializer_name}
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return {model}.objects.all()
        return self.queryset

"""
        
        # Escrever arquivo
        with open(views_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Views criadas para {app_name}")

if __name__ == "__main__":
    create_missing_views()
    print("🎉 Todas as views foram criadas!")