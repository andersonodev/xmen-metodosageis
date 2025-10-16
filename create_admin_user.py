#!/usr/bin/env python
"""
Script para criar usuário administrador no Sistema Ágil
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xmen_agileteam.settings')
django.setup()

from apps.accounts.models import User

def create_admin_user():
    """Cria um usuário administrador para teste"""
    try:
        # Tentar criar ou atualizar o usuário admin
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@exemplo.com',
                'first_name': 'Admin',
                'last_name': 'Sistema',
                'role': 'leader',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        
        # Definir senha
        user.set_password('admin123')
        user.save()
        
        if created:
            print("✅ Usuário admin criado com sucesso!")
        else:
            print("✅ Usuário admin atualizado com sucesso!")
            
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Nome: {user.get_full_name()}")
        print(f"   Role: {user.get_role_display()}")
        print("   Senha: admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        return False

if __name__ == '__main__':
    success = create_admin_user()
    sys.exit(0 if success else 1)