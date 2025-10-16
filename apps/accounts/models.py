from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modelo customizado de usuário para o sistema AgileTeam.
    """
    ROLE_CHOICES = [
        ('leader', 'Líder'),
        ('collaborator', 'Colaborador'),
    ]
    
    # Perfil do usuário
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='collaborator')
    bio = models.TextField(blank=True, null=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Informações profissionais
    position = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    # Disponibilidade
    availability_hours = models.PositiveIntegerField(
        default=8, 
        help_text="Horas disponíveis por dia"
    )
    is_available = models.BooleanField(default=True)
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return self.get_full_name() or self.username
        
    def is_leader(self):
        return self.role == 'leader'
        
    def is_collaborator(self):
        return self.role == 'collaborator'
