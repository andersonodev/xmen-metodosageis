#!/usr/bin/env python
"""
Script para criar usuários de teste no Sistema Ágil
Execute com: python manage.py shell < create_test_users.py
"""

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def create_test_users():
    """Cria os usuários de teste com username e senha iguais"""
    
    usuarios = [
        {
            'username': 'admin',
            'email': 'admin@sistemaagil.com',
            'first_name': 'Admin',
            'last_name': 'Sistema',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'lider',
            'email': 'lider@sistemaagil.com',
            'first_name': 'Líder',
            'last_name': 'Projeto'
        },
        {
            'username': 'colaborador',
            'email': 'colaborador@sistemaagil.com',
            'first_name': 'Colaborador',
            'last_name': 'Desenvolvedor'
        },
        {
            'username': 'product_owner',
            'email': 'product.owner@sistemaagil.com',
            'first_name': 'Product',
            'last_name': 'Owner'
        },
        {
            'username': 'scrum_master',
            'email': 'scrum.master@sistemaagil.com',
            'first_name': 'Scrum',
            'last_name': 'Master'
        },
        {
            'username': 'designer',
            'email': 'designer@sistemaagil.com',
            'first_name': 'Designer',
            'last_name': 'UX/UI'
        },
        {
            'username': 'qa_tester',
            'email': 'qa.tester@sistemaagil.com',
            'first_name': 'QA',
            'last_name': 'Tester'
        },
        {
            'username': 'devops',
            'email': 'devops@sistemaagil.com',
            'first_name': 'DevOps',
            'last_name': 'Engineer'
        },
        {
            'username': 'analista',
            'email': 'analista@sistemaagil.com',
            'first_name': 'Analista',
            'last_name': 'Sistemas'
        }
    ]

    print("🚀 Criando usuários de teste...")
    print("=" * 50)

    created_count = 0
    existing_count = 0

    with transaction.atomic():
        for usuario_data in usuarios:
            try:
                user, created = User.objects.get_or_create(
                    username=usuario_data['username'],
                    defaults={
                        'email': usuario_data['email'],
                        'first_name': usuario_data['first_name'],
                        'last_name': usuario_data['last_name'],
                        'is_staff': usuario_data.get('is_staff', False),
                        'is_superuser': usuario_data.get('is_superuser', False),
                        'is_active': True
                    }
                )
                
                if created:
                    # Senha igual ao username
                    user.set_password(usuario_data['username'])
                    user.save()
                    created_count += 1
                    print(f"✅ Usuário '{usuario_data['username']}' criado com sucesso!")
                else:
                    existing_count += 1
                    print(f"ℹ️  Usuário '{usuario_data['username']}' já existe")
                    
            except Exception as e:
                print(f"❌ Erro ao criar usuário '{usuario_data['username']}': {str(e)}")

    print("=" * 50)
    print(f"📊 Resumo:")
    print(f"   • Usuários criados: {created_count}")
    print(f"   • Usuários existentes: {existing_count}")
    print(f"   • Total processado: {len(usuarios)}")
    print("")
    print("🔐 Credenciais de acesso:")
    for usuario in usuarios:
        print(f"   • {usuario['username']} / {usuario['username']}")
    
    print("\n🎉 Processo concluído!")

if __name__ == "__main__":
    create_test_users()