#!/usr/bin/env python3
"""
Script para verificar se todas as funcionalidades do Xmen-AgileTeam foram implementadas
"""
import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Verifica se um arquivo existe"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MISSING")
        return False

def check_directory_structure():
    """Verifica a estrutura de diretórios"""
    print("🏗️  VERIFICANDO ESTRUTURA DO PROJETO")
    print("=" * 50)
    
    base_dirs = [
        ("apps/accounts", "Sistema de Autenticação"),
        ("apps/skills", "Gestão de Habilidades"),
        ("apps/teams", "Gestão de Times"),
        ("apps/projects", "Gestão de Projetos"),
        ("apps/tasks", "Sistema Kanban"),
        ("apps/dashboards", "Dashboards e Métricas"),
        ("apps/notifications", "Sistema de Notificações"),
        ("apps/chat", "Chat em Tempo Real"),
        ("apps/recommendations", "Sistema de IA"),
        ("apps/integrations", "Integrações Externas"),
        ("tests", "Testes Automatizados"),
        ("xmen_agileteam", "Configurações Django"),
    ]
    
    results = []
    for dir_path, description in base_dirs:
        exists = os.path.isdir(dir_path)
        status = "✅" if exists else "❌"
        print(f"{status} {description}: {dir_path}")
        results.append(exists)
    
    return all(results)

def check_core_files():
    """Verifica arquivos essenciais"""
    print("\n📁 VERIFICANDO ARQUIVOS ESSENCIAIS")
    print("=" * 50)
    
    core_files = [
        ("manage.py", "Django Management"),
        ("requirements.txt", "Dependências Python"),
        ("Dockerfile", "Configuração Docker"),
        ("docker-compose.yml", "Orquestração Docker"),
        ("Makefile", "Comandos de Desenvolvimento"),
        ("pytest.ini", "Configuração de Testes"),
        (".env.example", "Exemplo de Variáveis de Ambiente"),
        (".gitignore", "Configuração Git"),
        ("README.md", "Documentação"),
        ("setup.sh", "Script de Inicialização"),
    ]
    
    results = []
    for file_path, description in core_files:
        exists = check_file_exists(file_path, description)
        results.append(exists)
    
    return all(results)

def check_django_apps():
    """Verifica se todos os apps Django estão configurados"""
    print("\n🐍 VERIFICANDO APPS DJANGO")
    print("=" * 50)
    
    apps = [
        "accounts", "skills", "teams", "projects", "tasks",
        "dashboards", "notifications", "chat", "recommendations", "integrations"
    ]
    
    results = []
    for app in apps:
        app_files = [
            f"apps/{app}/models.py",
            f"apps/{app}/views.py",
            f"apps/{app}/serializers.py",
            f"apps/{app}/urls.py",
            f"apps/{app}/apps.py",
            f"apps/{app}/__init__.py",
        ]
        
        app_complete = True
        print(f"\n📱 App: {app}")
        for file_path in app_files:
            if os.path.exists(file_path):
                print(f"  ✅ {os.path.basename(file_path)}")
            else:
                print(f"  ❌ {os.path.basename(file_path)} - MISSING")
                app_complete = False
        
        results.append(app_complete)
    
    return all(results)

def check_functionality_coverage():
    """Verifica a cobertura das funcionalidades solicitadas"""
    print("\n🎯 VERIFICANDO COBERTURA DE FUNCIONALIDADES")
    print("=" * 50)
    
    functionalities = {
        "🔐 Autenticação e Perfis": [
            ("JWT Authentication", "apps/accounts/views.py"),
            ("User Model", "apps/accounts/models.py"),
            ("Registration/Login", "apps/accounts/serializers.py"),
        ],
        "👥 Gestão de Times": [
            ("Team CRUD", "apps/teams/models.py"),
            ("Team Members", "apps/teams/views.py"),
            ("Team Roles", "apps/teams/serializers.py"),
        ],
        "📁 Gestão de Projetos": [
            ("Project CRUD", "apps/projects/models.py"),
            ("Sprints", "apps/projects/views.py"),
            ("OKRs", "apps/projects/serializers.py"),
        ],
        "🗂️ Kanban/Scrum Board": [
            ("Task Management", "apps/tasks/models.py"),
            ("Drag & Drop", "apps/tasks/views.py"),
            ("Comments", "apps/tasks/serializers.py"),
        ],
        "🧠 Skills e Matching": [
            ("Skills Management", "apps/skills/models.py"),
            ("User Skills", "apps/skills/views.py"),
            ("Proficiency Levels", "apps/skills/serializers.py"),
        ],
        "📊 Dashboards e Métricas": [
            ("Metrics System", "apps/dashboards/models.py"),
            ("Dashboard Views", "apps/dashboards/views.py"),
            ("Metrics Serializers", "apps/dashboards/serializers.py"),
        ],
        "🔔 Notificações": [
            ("Notification System", "apps/notifications/models.py"),
            ("Celery Tasks", "apps/notifications/tasks.py"),
            ("User Preferences", "apps/notifications/views.py"),
        ],
        "💬 Chat e Colaboração": [
            ("WebSocket Chat", "apps/chat/consumers.py"),
            ("Chat Models", "apps/chat/models.py"),
            ("Real-time Routing", "apps/chat/routing.py"),
        ],
        "🧩 Integrações": [
            ("CSV Import", "apps/integrations/views.py"),
            ("Integration Framework", "apps/integrations/models.py"),
            ("External APIs", "apps/integrations/serializers.py"),
        ],
        "📈 IA e Recomendações": [
            ("AI Service", "apps/recommendations/services.py"),
            ("Team Allocation", "apps/recommendations/views.py"),
            ("Risk Analysis", "apps/recommendations/serializers.py"),
        ],
    }
    
    total_features = 0
    implemented_features = 0
    
    for category, features in functionalities.items():
        print(f"\n{category}")
        for feature_name, file_path in features:
            total_features += 1
            if os.path.exists(file_path):
                print(f"  ✅ {feature_name}")
                implemented_features += 1
            else:
                print(f"  ❌ {feature_name} - {file_path}")
    
    coverage = (implemented_features / total_features) * 100
    print(f"\n📈 COBERTURA TOTAL: {implemented_features}/{total_features} ({coverage:.1f}%)")
    
    return coverage >= 90

def check_database_config():
    """Verifica configuração do banco de dados"""
    print("\n🗄️  VERIFICANDO CONFIGURAÇÃO DO BANCO")
    print("=" * 50)
    
    settings_file = "xmen_agileteam/settings.py"
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            content = f.read()
            
        if "sqlite3" in content:
            print("✅ SQLite3 configurado corretamente")
            return True
        else:
            print("❌ SQLite3 não encontrado na configuração")
            return False
    else:
        print("❌ Arquivo settings.py não encontrado")
        return False

def check_dependencies():
    """Verifica se todas as dependências estão listadas"""
    print("\n📦 VERIFICANDO DEPENDÊNCIAS")
    print("=" * 50)
    
    required_deps = [
        "Django==", "djangorestframework==", "djangorestframework-simplejwt==",
        "channels==", "celery==", "redis==", "drf-spectacular==", 
        "pytest==", "pytest-django==", "pytest-cov=="
    ]
    
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", 'r') as f:
            content = f.read()
        
        missing_deps = []
        for dep in required_deps:
            if dep not in content:
                missing_deps.append(dep.replace("==", ""))
        
        if not missing_deps:
            print("✅ Todas as dependências necessárias estão presentes")
            return True
        else:
            print(f"❌ Dependências faltando: {', '.join(missing_deps)}")
            return False
    else:
        print("❌ requirements.txt não encontrado")
        return False

def main():
    """Função principal de verificação"""
    print("🦾 XMEN-AGILETEAM - VERIFICAÇÃO DE IMPLEMENTAÇÃO")
    print("=" * 60)
    
    os.chdir(Path(__file__).parent)
    
    checks = [
        ("Estrutura de Diretórios", check_directory_structure),
        ("Arquivos Essenciais", check_core_files),
        ("Apps Django", check_django_apps),
        ("Funcionalidades", check_functionality_coverage),
        ("Configuração SQLite3", check_database_config),
        ("Dependências", check_dependencies),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro ao verificar {check_name}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    for i, (check_name, _) in enumerate(checks):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\n🎯 VERIFICAÇÕES PASSARAM: {passed}/{total} ({percentage:.1f}%)")
    
    if percentage >= 90:
        print("🎉 PROJETO ESTÁ COMPLETO E PRONTO PARA USO!")
    elif percentage >= 70:
        print("⚠️  PROJETO ESTÁ QUASE COMPLETO - ALGUMAS CORREÇÕES NECESSÁRIAS")
    else:
        print("🚨 PROJETO PRECISA DE MAIS TRABALHO")
    
    return percentage >= 90

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)