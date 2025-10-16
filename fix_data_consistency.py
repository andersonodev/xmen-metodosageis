#!/usr/bin/env python
"""
Script para verificar e corrigir dados inconsistentes no banco de dados.
"""
import os
import sys
import django

# Setup Django
sys.path.append('/Users/anderson/my_folders/repositoriolocal/xmen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xmen_agileteam.settings')
django.setup()

from apps.tasks.models import Task
from apps.projects.models import Project

def check_data_consistency():
    """Verifica consistência dos dados"""
    print("=== Verificando Consistência dos Dados ===\n")
    
    # Verificar tasks com prioridades inválidas
    print("1. Verificando prioridades de tasks...")
    invalid_priority_tasks = Task.objects.exclude(priority__in=[1, 2, 3, 4])
    print(f"   Tasks com prioridade inválida: {invalid_priority_tasks.count()}")
    
    for task in invalid_priority_tasks:
        print(f"   - Task ID {task.id}: '{task.title}' tem prioridade '{task.priority}'")
    
    # Verificar tasks com status inválidos
    print("\n2. Verificando status de tasks...")
    valid_statuses = ['todo', 'in_progress', 'review', 'done']
    invalid_status_tasks = Task.objects.exclude(status__in=valid_statuses)
    print(f"   Tasks com status inválido: {invalid_status_tasks.count()}")
    
    for task in invalid_status_tasks:
        print(f"   - Task ID {task.id}: '{task.title}' tem status '{task.status}'")
    
    # Verificar projetos com prioridades inválidas
    print("\n3. Verificando prioridades de projetos...")
    invalid_priority_projects = Project.objects.exclude(priority__in=[1, 2, 3, 4])
    print(f"   Projetos com prioridade inválida: {invalid_priority_projects.count()}")
    
    for project in invalid_priority_projects:
        print(f"   - Projeto ID {project.id}: '{project.name}' tem prioridade '{project.priority}'")
    
    # Verificar projetos com status inválidos
    print("\n4. Verificando status de projetos...")
    valid_project_statuses = ['planning', 'active', 'on_hold', 'completed', 'cancelled']
    invalid_status_projects = Project.objects.exclude(status__in=valid_project_statuses)
    print(f"   Projetos com status inválido: {invalid_status_projects.count()}")
    
    for project in invalid_status_projects:
        print(f"   - Projeto ID {project.id}: '{project.name}' tem status '{project.status}'")

def fix_data_consistency():
    """Corrige dados inconsistentes"""
    print("\n=== Corrigindo Dados Inconsistentes ===\n")
    
    # Mapear valores antigos para novos
    priority_mapping = {
        'low': 1,
        'medium': 2,
        'normal': 2,
        'high': 3,
        'critical': 4,
        'critica': 4,
    }
    
    status_mapping = {
        'completed': 'done',
        'finished': 'done',
        'complete': 'done',
    }
    
    # Corrigir prioridades de tasks
    print("1. Corrigindo prioridades de tasks...")
    tasks_updated = 0
    for task in Task.objects.all():
        if isinstance(task.priority, str) and task.priority.lower() in priority_mapping:
            old_priority = task.priority
            task.priority = priority_mapping[task.priority.lower()]
            task.save()
            tasks_updated += 1
            print(f"   - Task '{task.title}': '{old_priority}' -> {task.priority}")
    
    print(f"   Total de tasks atualizadas: {tasks_updated}")
    
    # Corrigir status de tasks
    print("\n2. Corrigindo status de tasks...")
    status_updated = 0
    for task in Task.objects.all():
        if task.status in status_mapping:
            old_status = task.status
            task.status = status_mapping[task.status]
            task.save()
            status_updated += 1
            print(f"   - Task '{task.title}': '{old_status}' -> '{task.status}'")
    
    print(f"   Total de tasks atualizadas: {status_updated}")
    
    # Corrigir prioridades de projetos
    print("\n3. Corrigindo prioridades de projetos...")
    projects_updated = 0
    for project in Project.objects.all():
        if isinstance(project.priority, str) and project.priority.lower() in priority_mapping:
            old_priority = project.priority
            project.priority = priority_mapping[project.priority.lower()]
            project.save()
            projects_updated += 1
            print(f"   - Projeto '{project.name}': '{old_priority}' -> {project.priority}")
    
    print(f"   Total de projetos atualizados: {projects_updated}")

if __name__ == '__main__':
    check_data_consistency()
    
    response = input("\nDeseja corrigir os dados inconsistentes? (s/n): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        fix_data_consistency()
        print("\n=== Verificação Final ===")
        check_data_consistency()
    else:
        print("Nenhuma correção foi aplicada.")