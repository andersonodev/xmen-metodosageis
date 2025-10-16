from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.teams.models import Team, TeamMembership
from apps.skills.models import Skill, SkillCategory, UserSkill
from apps.projects.models import Project
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria usuários de exemplo para o sistema'

    def handle(self, *args, **options):
        self.stdout.write('Criando usuários de exemplo...')

        # Criar categorias de habilidades primeiro
        self.create_skill_categories()
        
        # Criar habilidades
        self.create_skills()

        # Criar Admin
        admin_charles = self.create_admin_charles()
        admin_scott = self.create_admin_scott()
        
        # Criar Leaders
        leader_jean = self.create_leader_jean()
        leader_logan = self.create_leader_logan()
        leader_ororo = self.create_leader_ororo()
        
        # Criar Collaborators
        collaborators = self.create_collaborators()
        
        # Criar Teams de exemplo
        self.create_example_teams()
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Usuários de exemplo criados com sucesso!')
        )
        self.stdout.write(
            self.style.SUCCESS('\n📋 Resumo dos usuários criados:')
        )
        self.stdout.write(f'  👨‍💼 Admins: 2 (charles.xavier, scott.summers)')
        self.stdout.write(f'  👥 Leaders: 3 (jean.grey, logan.wolverine, ororo.munroe)')
        self.stdout.write(f'  👨‍💻 Collaborators: 12')
        self.stdout.write(f'  🏆 Teams: 4 equipes de exemplo')
        self.stdout.write('\n💡 Acesse o sistema com qualquer usuário usando a senha "xmen2024"')

    def create_skill_categories(self):
        """Criar categorias de habilidades"""
        categories_data = [
            ('Frontend', 'Tecnologias de desenvolvimento frontend', '🎨'),
            ('Backend', 'Tecnologias de desenvolvimento backend', '⚙️'),
            ('DevOps', 'Infraestrutura e operações', '🔧'),
            ('Mobile', 'Desenvolvimento móvel', '📱'),
            ('Design', 'Design e experiência do usuário', '🎯'),
            ('Data Science', 'Ciência de dados e análise', '📊'),
            ('Comportamental', 'Habilidades interpessoais e comportamentais', '🤝'),
            ('Gestão', 'Gestão de projetos e equipes', '📋'),
            ('Negócio', 'Conhecimentos de negócio e estratégia', '💼'),
        ]
        
        for name, description, icon in categories_data:
            category, created = SkillCategory.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'icon': icon
                }
            )
            if created:
                self.stdout.write(f"  ✓ Categoria criada: {name}")
            else:
                self.stdout.write(f"  - Categoria já existe: {name}")
        
        self.stdout.write(self.style.SUCCESS('\n✅ Categorias de habilidades criadas com sucesso!'))

    def create_skills(self):
        """Criar habilidades de exemplo"""
        skills_data = [
            # Técnicas - Frontend
            ('React', 'Frontend', 'Biblioteca JavaScript para interfaces de usuário'),
            ('Vue.js', 'Frontend', 'Framework JavaScript progressivo'),
            ('Angular', 'Frontend', 'Framework TypeScript para aplicações web'),
            ('JavaScript', 'Frontend', 'Linguagem de programação para web'),
            ('TypeScript', 'Frontend', 'Superset do JavaScript com tipagem estática'),
            ('HTML/CSS', 'Frontend', 'Linguagens de marcação e estilo'),
            ('Sass/SCSS', 'Frontend', 'Extensão CSS com funcionalidades avançadas'),
            
            # Técnicas - Backend
            ('Python', 'Backend', 'Linguagem de programação versátil'),
            ('Django', 'Backend', 'Framework web Python'),
            ('FastAPI', 'Backend', 'Framework Python para APIs modernas'),
            ('Node.js', 'Backend', 'Runtime JavaScript para servidor'),
            ('Express.js', 'Backend', 'Framework web para Node.js'),
            ('PostgreSQL', 'Backend', 'Sistema de gerenciamento de banco de dados'),
            ('MongoDB', 'Backend', 'Banco de dados NoSQL'),
            ('Redis', 'Backend', 'Banco de dados em memória'),
            ('Docker', 'Backend', 'Plataforma de containerização'),
            ('Kubernetes', 'Backend', 'Orquestração de containers'),
            
            # Técnicas - DevOps
            ('AWS', 'DevOps', 'Serviços de nuvem Amazon'),
            ('Azure', 'DevOps', 'Serviços de nuvem Microsoft'),
            ('CI/CD', 'DevOps', 'Integração e entrega contínua'),
            ('GitHub Actions', 'DevOps', 'Automação de workflows'),
            ('Terraform', 'DevOps', 'Infraestrutura como código'),
            ('Ansible', 'DevOps', 'Automação de configuração'),
            
            # Técnicas - Mobile
            ('React Native', 'Mobile', 'Framework para desenvolvimento mobile'),
            ('Flutter', 'Mobile', 'SDK para desenvolvimento multiplataforma'),
            ('iOS Development', 'Mobile', 'Desenvolvimento para dispositivos Apple'),
            ('Android Development', 'Mobile', 'Desenvolvimento para Android'),
            
            # Técnicas - Design
            ('UI/UX Design', 'Design', 'Design de interfaces e experiência do usuário'),
            ('Figma', 'Design', 'Ferramenta de design colaborativo'),
            ('Adobe Creative Suite', 'Design', 'Pacote de ferramentas de design'),
            ('Prototyping', 'Design', 'Criação de protótipos interativos'),
            
            # Técnicas - Data Science
            ('Machine Learning', 'Data Science', 'Aprendizado de máquina'),
            ('Data Analysis', 'Data Science', 'Análise de dados'),
            ('Python Data Stack', 'Data Science', 'Pandas, NumPy, Scikit-learn'),
            ('SQL', 'Data Science', 'Linguagem de consulta estruturada'),
            ('Tableau', 'Data Science', 'Ferramenta de visualização de dados'),
            ('Power BI', 'Data Science', 'Plataforma de business intelligence'),
            
            # Comportamentais
            ('Liderança', 'Comportamental', 'Capacidade de liderar equipes'),
            ('Comunicação', 'Comportamental', 'Habilidades de comunicação eficaz'),
            ('Trabalho em Equipe', 'Comportamental', 'Colaboração e sinergia'),
            ('Resolução de Problemas', 'Comportamental', 'Análise e solução de desafios'),
            ('Pensamento Crítico', 'Comportamental', 'Análise objetiva e racional'),
            ('Adaptabilidade', 'Comportamental', 'Flexibilidade a mudanças'),
            ('Gestão de Tempo', 'Comportamental', 'Organização e priorização'),
            ('Mentoring', 'Comportamental', 'Orientação e desenvolvimento de pessoas'),
            ('Negociação', 'Comportamental', 'Habilidades de negociação'),
            ('Apresentação', 'Comportamental', 'Comunicação pública eficaz'),
            
            # Gestão
            ('Gestão de Projetos', 'Gestão', 'Planejamento e execução de projetos'),
            ('Scrum', 'Gestão', 'Framework ágil para desenvolvimento'),
            ('Kanban', 'Gestão', 'Método visual de gestão de workflow'),
            ('Product Management', 'Gestão', 'Gestão de produtos digitais'),
            ('Agile Methodologies', 'Gestão', 'Metodologias ágeis de desenvolvimento'),
            ('Risk Management', 'Gestão', 'Gestão e mitigação de riscos'),
            ('Stakeholder Management', 'Gestão', 'Gestão de partes interessadas'),
            ('Budget Planning', 'Gestão', 'Planejamento orçamentário'),
            
            # Negócio
            ('Business Analysis', 'Negócio', 'Análise de processos de negócio'),
            ('Market Research', 'Negócio', 'Pesquisa e análise de mercado'),
            ('Strategic Planning', 'Negócio', 'Planejamento estratégico'),
            ('Customer Success', 'Negócio', 'Sucesso do cliente'),
            ('Sales', 'Negócio', 'Vendas e desenvolvimento comercial'),
            ('Marketing Digital', 'Negócio', 'Estratégias de marketing digital'),
            ('Content Strategy', 'Negócio', 'Estratégia de conteúdo'),
            ('Financial Analysis', 'Negócio', 'Análise financeira'),
        ]
        
        for skill_name, category_name, description in skills_data:
            try:
                category = SkillCategory.objects.get(name=category_name)
                skill, created = Skill.objects.get_or_create(
                    name=skill_name,
                    category=category,
                    defaults={
                        'description': description,
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f"  ✓ Habilidade criada: {skill_name}")
                else:
                    self.stdout.write(f"  - Habilidade já existe: {skill_name}")
            except SkillCategory.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"  ✗ Categoria não encontrada: {category_name}"))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Habilidades criadas com sucesso!'))

    def create_admin_charles(self):
        """Criar Charles Xavier - Admin Principal"""
        username = 'charles.xavier'
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  - Admin já existe: {username}")
            return User.objects.get(username=username)
        
        admin = User.objects.create_user(
            username=username,
            email='charles@xmen.com',
            password='xmen2024',
            first_name='Charles',
            last_name='Xavier',
            is_staff=True,
            is_superuser=True,
            role='admin'
        )
        self.stdout.write(f"  ✓ Admin criado: {username}")
        
        # Adicionar skills de liderança e gestão
        self.assign_user_skills(admin, [
            ('Liderança', 5),
            ('Gestão de Projetos', 5),
            ('Strategic Planning', 5),
            ('Mentoring', 5),
            ('Comunicação', 5),
            ('Scrum', 4),
            ('Business Analysis', 4),
        ])
        
        return admin

    def create_admin_scott(self):
        """Criar Scott Summers - Admin Operacional"""
        username = 'scott.summers'
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  - Admin já existe: {username}")
            return User.objects.get(username=username)
        
        admin = User.objects.create_user(
            username=username,
            email='scott@xmen.com',
            password='xmen2024',
            first_name='Scott',
            last_name='Summers',
            is_staff=True,
            is_superuser=True,
            role='admin'
        )
        self.stdout.write(f"  ✓ Admin criado: {username}")
        
        # Adicionar skills operacionais e técnicas
        self.assign_user_skills(admin, [
            ('Gestão de Projetos', 5),
            ('Agile Methodologies', 5),
            ('Risk Management', 4),
            ('Scrum', 5),
            ('Kanban', 4),
            ('CI/CD', 3),
            ('AWS', 3),
        ])
        
        return admin

    def create_leader_jean(self):
        """Criar Jean Grey - Team Leader Frontend"""
        username = 'jean.grey'
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  - Leader já existe: {username}")
            return User.objects.get(username=username)
        
        leader = User.objects.create_user(
            username=username,
            email='jean@xmen.com',
            password='xmen2024',
            first_name='Jean',
            last_name='Grey',
            role='leader'
        )
        self.stdout.write(f"  ✓ Leader criado: {username}")
        
        # Skills de frontend e liderança
        self.assign_user_skills(leader, [
            ('React', 5),
            ('JavaScript', 5),
            ('TypeScript', 4),
            ('HTML/CSS', 5),
            ('UI/UX Design', 4),
            ('Liderança', 4),
            ('Mentoring', 4),
            ('Scrum', 4),
        ])
        
        return leader

    def create_leader_logan(self):
        """Criar Logan/Wolverine - Team Leader Backend"""
        username = 'logan.wolverine'
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  - Leader já existe: {username}")
            return User.objects.get(username=username)
        
        leader = User.objects.create_user(
            username=username,
            email='logan@xmen.com',
            password='xmen2024',
            first_name='Logan',
            last_name='Wolverine',
            role='leader'
        )
        self.stdout.write(f"  ✓ Leader criado: {username}")
        
        # Skills de backend e devops
        self.assign_user_skills(leader, [
            ('Python', 5),
            ('Django', 5),
            ('PostgreSQL', 4),
            ('Docker', 4),
            ('AWS', 3),
            ('Redis', 3),
            ('Liderança', 4),
            ('Resolução de Problemas', 5),
        ])
        
        return leader

    def create_leader_ororo(self):
        """Criar Ororo Munroe - Team Leader DevOps"""
        username = 'ororo.munroe'
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  - Leader já existe: {username}")
            return User.objects.get(username=username)
        
        leader = User.objects.create_user(
            username=username,
            email='ororo@xmen.com',
            password='xmen2024',
            first_name='Ororo',
            last_name='Munroe',
            role='leader'
        )
        self.stdout.write(f"  ✓ Leader criado: {username}")
        
        # Skills de DevOps e infraestrutura
        self.assign_user_skills(leader, [
            ('AWS', 5),
            ('Docker', 5),
            ('Kubernetes', 4),
            ('CI/CD', 5),
            ('Terraform', 4),
            ('Ansible', 3),
            ('Liderança', 4),
            ('Gestão de Projetos', 3),
        ])
        
        return leader

    def create_collaborators(self):
        """Criar colaboradores com diferentes especialidades"""
        collaborators_data = [
            # Frontend Developers
            ('kurt.wagner', 'Kurt', 'Wagner', 'kurt@xmen.com', [
                ('React', 4), ('JavaScript', 4), ('HTML/CSS', 4), ('Sass/SCSS', 3)
            ]),
            ('kitty.pryde', 'Kitty', 'Pryde', 'kitty@xmen.com', [
                ('Vue.js', 4), ('JavaScript', 4), ('TypeScript', 3), ('UI/UX Design', 3)
            ]),
            ('bobby.drake', 'Bobby', 'Drake', 'bobby@xmen.com', [
                ('Angular', 4), ('TypeScript', 4), ('JavaScript', 4), ('HTML/CSS', 3)
            ]),
            
            # Backend Developers
            ('remy.lebeau', 'Remy', 'LeBeau', 'remy@xmen.com', [
                ('Python', 4), ('Django', 4), ('PostgreSQL', 3), ('Redis', 3)
            ]),
            ('warren.worthington', 'Warren', 'Worthington III', 'warren@xmen.com', [
                ('Node.js', 4), ('Express.js', 4), ('MongoDB', 3), ('JavaScript', 4)
            ]),
            ('piotr.rasputin', 'Piotr', 'Rasputin', 'piotr@xmen.com', [
                ('FastAPI', 3), ('Python', 4), ('Docker', 3), ('PostgreSQL', 3)
            ]),
            
            # Mobile/Fullstack
            ('alex.summers', 'Alex', 'Summers', 'alex@xmen.com', [
                ('React Native', 4), ('JavaScript', 4), ('React', 3), ('iOS Development', 4)
            ]),
            ('betsy.braddock', 'Betsy', 'Braddock', 'betsy@xmen.com', [
                ('Flutter', 4), ('Android Development', 4), ('UI/UX Design', 3), ('Prototyping', 3)
            ]),
            
            # DevOps/Infrastructure
            ('erik.lehnsherr', 'Erik', 'Lehnsherr', 'erik@xmen.com', [
                ('AWS', 4), ('Terraform', 4), ('CI/CD', 4), ('Docker', 3)
            ]),
            ('hank.mccoy', 'Hank', 'McCoy', 'hank@xmen.com', [
                ('Azure', 3), ('Kubernetes', 4), ('CI/CD', 4), ('Ansible', 3)
            ]),
            
            # Design/UX
            ('jubilee.lee', 'Jubilee', 'Lee', 'jubilee@xmen.com', [
                ('UI/UX Design', 4), ('Figma', 4), ('Prototyping', 4), ('Adobe Creative Suite', 3)
            ]),
            
            # Data Science
            ('emma.frost', 'Emma', 'Frost', 'emma@xmen.com', [
                ('Data Analysis', 4), ('Python Data Stack', 4), ('SQL', 4), ('Machine Learning', 3)
            ]),
        ]
        
        created_collaborators = []
        
        for username, first_name, last_name, email, skills in collaborators_data:
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"  - Collaborator já existe: {username}")
                user = User.objects.get(username=username)
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='xmen2024',
                    first_name=first_name,
                    last_name=last_name,
                    role='collaborator'
                )
                self.stdout.write(f"  ✓ Collaborator criado: {username}")
            
            # Adicionar skills específicas
            self.assign_user_skills(user, skills)
            created_collaborators.append(user)
        
        return created_collaborators

    def assign_user_skills(self, user, skills_data):
        """Atribuir habilidades a um usuário"""
        for skill_name, level in skills_data:
            try:
                skill = Skill.objects.get(name=skill_name)
                user_skill, created = UserSkill.objects.get_or_create(
                    user=user,
                    skill=skill,
                    defaults={'level': level}
                )
                if not created:
                    user_skill.level = level
                    user_skill.save()
            except Skill.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠️  Skill não encontrada: {skill_name}")
                )

    def create_example_teams(self):
        """Criar times de exemplo"""
        teams_data = [
            {
                'name': 'Frontend Avengers',
                'description': 'Time especializado em desenvolvimento frontend moderno',
                'leader': 'jean.grey',
                'members': ['kurt.wagner', 'kitty.pryde', 'bobby.drake', 'jubilee.lee']
            },
            {
                'name': 'Backend Force',
                'description': 'Time focado em APIs robustas e arquitetura backend',
                'leader': 'logan.wolverine',
                'members': ['remy.lebeau', 'warren.worthington', 'piotr.rasputin']
            },
            {
                'name': 'DevOps Storm',
                'description': 'Time de infraestrutura e operações',
                'leader': 'ororo.munroe',
                'members': ['erik.lehnsherr', 'hank.mccoy']
            },
            {
                'name': 'Mobile Mutants',
                'description': 'Time de desenvolvimento mobile multiplataforma',
                'leader': 'jean.grey',  # Jean pode liderar múltiplos times
                'members': ['alex.summers', 'betsy.braddock', 'emma.frost']
            }
        ]
        
        for team_data in teams_data:
            team_name = team_data['name']
            
            if Team.objects.filter(name=team_name).exists():
                self.stdout.write(f"  - Time já existe: {team_name}")
                continue
            
            # Buscar o leader
            try:
                leader = User.objects.get(username=team_data['leader'])
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Leader não encontrado: {team_data['leader']}")
                )
                continue
            
            # Criar o time
            team = Team.objects.create(
                name=team_name,
                description=team_data['description'],
                created_by=leader,
                is_active=True
            )
            
            # Adicionar o leader como membro líder
            TeamMembership.objects.create(
                team=team,
                user=leader,
                role='scrum_master',
                is_lead=True
            )
            
            # Adicionar membros
            for member_username in team_data['members']:
                try:
                    member = User.objects.get(username=member_username)
                    TeamMembership.objects.create(
                        team=team,
                        user=member,
                        role='developer'
                    )
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠️  Membro não encontrado: {member_username}")
                    )
            
            self.stdout.write(f"  ✓ Time criado: {team_name} ({len(team_data['members'])} membros)")
        
        self.stdout.write(self.style.SUCCESS('\n✅ Times de exemplo criados com sucesso!'))