from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.skills.models import SkillCategory, Skill, UserSkill
from apps.teams.models import Team, TeamMembership
from apps.projects.models import Project, ProjectTemplate, Sprint
from apps.tasks.models import Column, Task
from apps.notifications.models import NotificationPreference
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando seed de dados...'))
        
        # Limpar dados existentes (opcional)
        if input("Deseja limpar dados existentes? (y/N): ").lower() == 'y':
            self.clear_data()
        
        # Criar dados
        self.create_users()
        self.create_skill_categories_and_skills()
        self.create_user_skills()
        self.create_teams()
        self.create_projects()
        self.create_tasks()
        self.create_preferences()
        
        self.stdout.write(self.style.SUCCESS('Seed de dados concluído com sucesso!'))
    
    def clear_data(self):
        """Limpar dados existentes (cuidado em produção!)"""
        self.stdout.write('Limpando dados existentes...')
        
        # Ordem importante devido às foreign keys
        Task.objects.all().delete()
        Column.objects.all().delete()
        Sprint.objects.all().delete()
        Project.objects.all().delete()
        ProjectTemplate.objects.all().delete()
        TeamMembership.objects.all().delete()
        Team.objects.all().delete()
        UserSkill.objects.all().delete()
        Skill.objects.all().delete()
        SkillCategory.objects.all().delete()
        NotificationPreference.objects.all().delete()
        
        # Não deletar superusers
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.WARNING('Dados limpos!'))
    
    def create_users(self):
        """Criar usuários de exemplo"""
        self.stdout.write('Criando usuários...')
        
        # Líder
        leader = User.objects.create_user(
            username='leader1',
            email='leader@xmen.com',
            password='123456',
            first_name='Charles',
            last_name='Xavier',
            role='leader',
            position='Tech Lead',
            department='Desenvolvimento',
            bio='Líder experiente em metodologias ágeis e formação de times.'
        )
        
        # Colaboradores
        collaborators_data = [
            {
                'username': 'wolverine',
                'email': 'logan@xmen.com',
                'first_name': 'Logan',
                'last_name': 'Howlett',
                'position': 'Senior Developer',
                'bio': 'Desenvolvedor full-stack com foco em backend.'
            },
            {
                'username': 'storm',
                'email': 'ororo@xmen.com',
                'first_name': 'Ororo',
                'last_name': 'Monroe',
                'position': 'Frontend Developer',
                'bio': 'Especialista em UX/UI e desenvolvimento frontend.'
            },
            {
                'username': 'cyclops',
                'email': 'scott@xmen.com',
                'first_name': 'Scott',
                'last_name': 'Summers',
                'position': 'Scrum Master',
                'bio': 'Scrum Master certificado com experiência em agilidade.'
            },
            {
                'username': 'jean',
                'email': 'jean@xmen.com',
                'first_name': 'Jean',
                'last_name': 'Grey',
                'position': 'Product Owner',
                'bio': 'Product Owner com background em análise de negócios.'
            },
            {
                'username': 'nightcrawler',
                'email': 'kurt@xmen.com',
                'first_name': 'Kurt',
                'last_name': 'Wagner',
                'position': 'QA Engineer',
                'bio': 'Especialista em testes automatizados e qualidade.'
            }
        ]
        
        for data in collaborators_data:
            User.objects.create_user(
                password='123456',
                role='collaborator',
                department='Desenvolvimento',
                **data
            )
        
        self.stdout.write(f'✓ Criados {len(collaborators_data) + 1} usuários')
    
    def create_skill_categories_and_skills(self):
        """Criar categorias e habilidades"""
        self.stdout.write('Criando habilidades...')
        
        categories_data = [
            {
                'name': 'Técnicas',
                'description': 'Habilidades técnicas de desenvolvimento',
                'icon': 'code',
                'skills': [
                    'Python', 'JavaScript', 'React', 'Django', 'Node.js',
                    'PostgreSQL', 'MongoDB', 'Docker', 'Kubernetes', 'AWS'
                ]
            },
            {
                'name': 'Metodologias',
                'description': 'Metodologias ágeis e práticas',
                'icon': 'agile',
                'skills': [
                    'Scrum', 'Kanban', 'SAFe', 'Design Thinking', 'Lean'
                ]
            },
            {
                'name': 'Soft Skills',
                'description': 'Habilidades comportamentais',
                'icon': 'people',
                'skills': [
                    'Liderança', 'Comunicação', 'Trabalho em Equipe',
                    'Resolução de Problemas', 'Adaptabilidade'
                ]
            },
            {
                'name': 'Negócio',
                'description': 'Conhecimentos de negócio',
                'icon': 'business',
                'skills': [
                    'Análise de Negócio', 'Product Management', 'UX Research',
                    'Data Analysis', 'Customer Journey'
                ]
            }
        ]
        
        for cat_data in categories_data:
            skills_list = cat_data.pop('skills')
            category = SkillCategory.objects.create(**cat_data)
            
            for skill_name in skills_list:
                Skill.objects.create(
                    name=skill_name,
                    category=category,
                    description=f'Habilidade em {skill_name}'
                )
        
        self.stdout.write('✓ Categorias e habilidades criadas')
    
    def create_user_skills(self):
        """Atribuir habilidades aos usuários"""
        self.stdout.write('Atribuindo habilidades aos usuários...')
        
        users = User.objects.filter(role='collaborator')
        skills = Skill.objects.all()
        
        # Mapeamento específico para demonstração
        skill_assignments = {
            'wolverine': ['Python', 'Django', 'PostgreSQL', 'Docker', 'Scrum'],
            'storm': ['JavaScript', 'React', 'UX Research', 'Design Thinking'],
            'cyclops': ['Scrum', 'Kanban', 'Liderança', 'Facilitação'],
            'jean': ['Product Management', 'Análise de Negócio', 'UX Research'],
            'nightcrawler': ['Python', 'JavaScript', 'Testes Automatizados']
        }
        
        for user in users:
            assigned_skills = skill_assignments.get(user.username, [])
            
            for skill_name in assigned_skills:
                try:
                    skill = skills.get(name=skill_name)
                    level = random.randint(3, 5)  # Níveis 3-5 para demonstração
                    
                    UserSkill.objects.create(
                        user=user,
                        skill=skill,
                        level=level
                    )
                except Skill.DoesNotExist:
                    continue
            
            # Adicionar algumas skills aleatórias
            random_skills = random.sample(list(skills), 3)
            for skill in random_skills:
                if not UserSkill.objects.filter(user=user, skill=skill).exists():
                    UserSkill.objects.create(
                        user=user,
                        skill=skill,
                        level=random.randint(2, 4)
                    )
        
        self.stdout.write('✓ Habilidades atribuídas aos usuários')
    
    def create_teams(self):
        """Criar times de exemplo"""
        self.stdout.write('Criando times...')
        
        leader = User.objects.get(username='leader1')
        
        # Time X-Men
        team = Team.objects.create(
            name='X-Men Squad',
            description='Time multidisciplinar focado em desenvolvimento de produtos',
            max_members=8,
            created_by=leader
        )
        
        # Adicionar membros ao time
        members_data = [
            {'username': 'cyclops', 'role': 'scrum_master', 'is_lead': True},
            {'username': 'jean', 'role': 'product_owner'},
            {'username': 'wolverine', 'role': 'developer'},
            {'username': 'storm', 'role': 'developer'},
            {'username': 'nightcrawler', 'role': 'qa'},
        ]
        
        for member_data in members_data:
            user = User.objects.get(username=member_data['username'])
            TeamMembership.objects.create(
                team=team,
                user=user,
                role=member_data['role'],
                is_lead=member_data.get('is_lead', False),
                allocation_percentage=100
            )
        
        self.stdout.write('✓ Time criado com membros')
    
    def create_projects(self):
        """Criar projetos de exemplo"""
        self.stdout.write('Criando projetos...')
        
        team = Team.objects.first()
        leader = User.objects.get(username='leader1')
        
        # Template de projeto
        template = ProjectTemplate.objects.create(
            name='Desenvolvimento Web',
            description='Template para projetos de desenvolvimento web',
            default_duration_days=90,
            default_team_size=5
        )
        
        # Projeto principal
        from datetime import date, timedelta
        
        project = Project.objects.create(
            name='Sistema de Gestão AgileTeam',
            description='Desenvolvimento do sistema de gestão de times ágeis',
            status='active',
            priority=3,
            team=team,
            template=template,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            estimated_hours=720,
            created_by=leader
        )
        
        # Sprint
        sprint = Sprint.objects.create(
            project=project,
            name='Sprint 1 - MVP',
            goal='Desenvolver funcionalidades básicas do MVP',
            status='active',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14),
            planned_points=30
        )
        
        self.stdout.write('✓ Projeto e sprint criados')
    
    def create_tasks(self):
        """Criar tarefas e colunas Kanban"""
        self.stdout.write('Criando tarefas...')
        
        project = Project.objects.first()
        sprint = Sprint.objects.first()
        
        # Criar colunas do Kanban
        columns_data = [
            {'name': 'Backlog', 'position': 1, 'color': '#6B73FF'},
            {'name': 'To Do', 'position': 2, 'color': '#FFD93D'},
            {'name': 'In Progress', 'position': 3, 'color': '#6BCF7F', 'wip_limit': 3},
            {'name': 'Review', 'position': 4, 'color': '#FF6B6B'},
            {'name': 'Done', 'position': 5, 'color': '#4ECDC4', 'is_done_column': True},
        ]
        
        columns = []
        for col_data in columns_data:
            column = Column.objects.create(project=project, **col_data)
            columns.append(column)
        
        # Criar tarefas
        users = list(User.objects.filter(role='collaborator'))
        todo_column = columns[1]  # To Do
        progress_column = columns[2]  # In Progress
        done_column = columns[4]  # Done
        
        tasks_data = [
            {
                'title': 'Configurar ambiente de desenvolvimento',
                'description': 'Setup inicial do projeto Django com Docker',
                'type': 'task',
                'priority': 4,
                'column': done_column,
                'status': 'done',
                'story_points': 5,
                'assignee': User.objects.get(username='wolverine')
            },
            {
                'title': 'Implementar autenticação JWT',
                'description': 'Sistema de login e registro com tokens JWT',
                'type': 'story',
                'priority': 3,
                'column': progress_column,
                'status': 'in_progress',
                'story_points': 8,
                'assignee': User.objects.get(username='wolverine')
            },
            {
                'title': 'Criar interface de dashboard',
                'description': 'Dashboard principal com métricas do projeto',
                'type': 'story',
                'priority': 2,
                'column': todo_column,
                'status': 'todo',
                'story_points': 13,
                'assignee': User.objects.get(username='storm')
            },
            {
                'title': 'Implementar quadro Kanban',
                'description': 'Quadro interativo com drag & drop',
                'type': 'story',
                'priority': 3,
                'column': todo_column,
                'status': 'todo',
                'story_points': 21,
                'assignee': User.objects.get(username='storm')
            },
            {
                'title': 'Configurar testes automatizados',
                'description': 'Setup do pytest e testes unitários',
                'type': 'task',
                'priority': 2,
                'column': todo_column,
                'status': 'todo',
                'story_points': 8,
                'assignee': User.objects.get(username='nightcrawler')
            }
        ]
        
        for i, task_data in enumerate(tasks_data):
            Task.objects.create(
                project=project,
                sprint=sprint,
                position=i,
                created_by=User.objects.get(username='leader1'),
                **task_data
            )
        
        self.stdout.write('✓ Colunas e tarefas criadas')
    
    def create_preferences(self):
        """Criar preferências de notificação"""
        self.stdout.write('Criando preferências...')
        
        for user in User.objects.all():
            NotificationPreference.objects.create(
                user=user,
                task_assigned_email=True,
                task_assigned_push=True,
                task_due_email=True,
                task_due_push=True,
                project_update_email=False,
                project_update_push=True,
                team_invitation_email=True,
                team_invitation_push=True,
                email_frequency='immediate'
            )
        
        self.stdout.write('✓ Preferências criadas')


if __name__ == '__main__':
    # Para poder executar como script standalone
    import django
    import os
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xmen_agileteam.settings')
    django.setup()
    
    command = Command()
    command.handle()