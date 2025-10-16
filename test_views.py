#!/usr/bin/env python
"""
Script para testar as views corrigidas diretamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xmen_agileteam.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.projects.views import project_list
from apps.teams.views import team_list
from apps.notifications.views import notification_list
from apps.chat.views import chat_rooms
from apps.integrations.views import integration_list

User = get_user_model()

def test_views():
    """Testar todas as views corrigidas"""
    # Criar request factory e usuário de teste
    factory = RequestFactory()
    user = User.objects.first()
    
    if not user:
        print("❌ Nenhum usuário encontrado para testar")
        return
    
    print(f"🧪 Testando views com usuário: {user.username}")
    
    # Testar view de projetos
    try:
        request = factory.get('/projects/')
        request.user = user
        response = project_list(request)
        print(f"✅ Projects view: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Projects view: {str(e)}")
    
    # Testar view de teams
    try:
        request = factory.get('/teams/')
        request.user = user
        response = team_list(request)
        print(f"✅ Teams view: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Teams view: {str(e)}")
    
    # Testar view de notifications
    try:
        request = factory.get('/notifications/')
        request.user = user
        response = notification_list(request)
        print(f"✅ Notifications view: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Notifications view: {str(e)}")
    
    # Testar view de chat
    try:
        request = factory.get('/chat/')
        request.user = user
        response = chat_rooms(request)
        print(f"✅ Chat view: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Chat view: {str(e)}")
    
    # Testar view de integrations
    try:
        request = factory.get('/integrations/')
        request.user = user
        response = integration_list(request)
        print(f"✅ Integrations view: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Integrations view: {str(e)}")

if __name__ == '__main__':
    test_views()