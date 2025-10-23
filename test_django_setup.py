#!/usr/bin/env python3
"""
Script para corrigir automaticamente todos os problemas de setup do Django
"""

import os
import sys
import traceback
from pathlib import Path

# Configurar o ambiente Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.chdir(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xmen_agileteam.settings')

try:
    import django
    django.setup()
    print("✅ Django configurado com sucesso!")
    
    # Importar apps para testar
    print("\n🔍 Testando imports dos apps...")
    
    from apps.accounts.models import User
    print("✅ accounts.models - OK")
    
    from apps.skills.models import Skill, SkillCategory, UserSkill
    print("✅ skills.models - OK")
    
    from apps.teams.models import Team, TeamMembership, TeamInvitation
    print("✅ teams.models - OK")
    
    from apps.projects.models import Project, Sprint, OKR
    print("✅ projects.models - OK")
    
    from apps.tasks.models import Task, Column, TaskComment
    print("✅ tasks.models - OK")
    
    from apps.dashboards.models import MetricSnapshot, ProjectReport, DashboardWidget
    print("✅ dashboards.models - OK")
    
    from apps.notifications.models import Notification, NotificationPreference
    print("✅ notifications.models - OK")
    
    from apps.chat.models import ChatRoom, Message
    print("✅ chat.models - OK")
    
    from apps.recommendations.models import Recommendation
    print("✅ recommendations.models - OK")
    
    from apps.integrations.models import Integration, ImportHistory
    print("✅ integrations.models - OK")
    
    print("\n🎯 Executando makemigrations...")
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    print("\n🎉 Migrações criadas com sucesso!")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    print("\n📋 Stack trace completo:")
    traceback.print_exc()
