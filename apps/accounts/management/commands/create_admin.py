from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import CommandError
import getpass

User = get_user_model()


class Command(BaseCommand):
    """
    Comando para criar um superusuário admin com dados padrão.
    """
    help = 'Cria um superusuário admin para o sistema'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='admin',
            help='Username do admin (padrão: admin)'
        )
        parser.add_argument(
            '--email',
            default='admin@xmen-agileteam.com',
            help='Email do admin (padrão: admin@xmen-agileteam.com)'
        )
        parser.add_argument(
            '--password',
            help='Senha do admin (se não fornecida, será solicitada)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a criação mesmo se o usuário já existir'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        force = options['force']
        
        # Verificar se usuário já existe
        if User.objects.filter(username=username).exists():
            if not force:
                raise CommandError(f'Usuário "{username}" já existe. Use --force para sobrescrever.')
            else:
                # Deletar usuário existente
                User.objects.filter(username=username).delete()
                self.stdout.write(
                    self.style.WARNING(f'Usuário "{username}" existente foi removido.')
                )
        
        # Solicitar senha se não fornecida
        if not password:
            password = getpass.getpass('Senha do admin: ')
            password_confirm = getpass.getpass('Confirme a senha: ')
            
            if password != password_confirm:
                raise CommandError('Senhas não coincidem.')
        
        # Criar superusuário
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Admin',
            last_name='Sistema',
            role='leader',
            position='Administrador do Sistema',
            department='TI',
            bio='Administrador principal do sistema Xmen-AgileTeam',
            is_available=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Superusuário "{username}" criado com sucesso!\n'
                f'   Email: {email}\n'
                f'   Acesse: http://localhost:8000/admin/\n'
                f'   Username: {username}\n'
                f'   Password: [senha fornecida]'
            )
        )