from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Team(models.Model):
    """
    Modelo para representar um time/squad.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Configurações do time
    max_members = models.PositiveIntegerField(default=8)
    is_active = models.BooleanField(default=True)
    
    # Metadados
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_teams'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teams'
        verbose_name = 'Time'
        verbose_name_plural = 'Times'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        return self.memberships.filter(is_active=True).count()
    
    @property
    def is_full(self):
        return self.member_count >= self.max_members


class TeamMembership(models.Model):
    """
    Relacionamento entre usuário e time com papel específico.
    """
    ROLE_CHOICES = [
        ('product_owner', 'Product Owner'),
        ('scrum_master', 'Scrum Master'),
        ('developer', 'Desenvolvedor'),
        ('designer', 'Designer'),
        ('qa', 'QA/Tester'),
        ('devops', 'DevOps'),
        ('analyst', 'Analista'),
        ('other', 'Outro'),
    ]
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='developer')
    
    # Status da participação
    is_active = models.BooleanField(default=True)
    is_lead = models.BooleanField(default=False)
    
    # Capacidade e disponibilidade
    allocation_percentage = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Percentual de alocação no time (1-100%)"
    )
    
    # Metadados
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'team_memberships'
        verbose_name = 'Membro do Time'
        verbose_name_plural = 'Membros dos Times'
        unique_together = ['team', 'user']
        ordering = ['-is_lead', 'role', 'joined_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.get_role_display()})"


class TeamInvitation(models.Model):
    """
    Convite para participar de um time.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('accepted', 'Aceito'),
        ('declined', 'Recusado'),
        ('expired', 'Expirado'),
    ]
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    invited_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_invitations'
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_team_invitations'
    )
    
    proposed_role = models.CharField(
        max_length=20, 
        choices=TeamMembership.ROLE_CHOICES,
        default='developer'
    )
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'team_invitations'
        verbose_name = 'Convite para Time'
        verbose_name_plural = 'Convites para Times'
        unique_together = ['team', 'invited_user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Convite: {self.invited_user.username} para {self.team.name}"
