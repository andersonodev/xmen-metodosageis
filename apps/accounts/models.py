from __future__ import annotations

import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .encryption import decrypt, encrypt


class EncryptedTextField(models.TextField):
    """Text field that transparently encrypts values using Fernet."""

    def from_db_value(self, value, expression, connection):  # pragma: no cover - delegated behaviour
        if value is None:
            return value
        decrypted = decrypt(value)
        return decrypted if decrypted is not None else ""

    def to_python(self, value):
        if value is None:
            return value
        # Values coming from forms or the ORM after ``from_db_value`` are plain strings
        # whereas values passed programmatically may still be encrypted. We try to
        # decrypt and, if that fails, assume the value is already decrypted.
        decrypted = decrypt(value)
        return decrypted if decrypted is not None else value

    def get_prep_value(self, value):
        if value in (None, ""):
            return value
        return encrypt(value)


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
    bio = EncryptedTextField(blank=True, null=True, max_length=500)
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

    @property
    def is_email_verified(self) -> bool:
        pending_tokens = self.verification_tokens.filter(
            confirmed_at__isnull=True,
            expires_at__gt=timezone.now(),
        ).exists()
        has_confirmed = self.verification_tokens.filter(confirmed_at__isnull=False).exists()

        if self.verification_tokens.count() == 0:
            # Legacy accounts created prior to the verification flow are
            # considered verified so that administrators are not locked out.
            return True

        return has_confirmed and not pending_tokens


class EmailVerificationToken(models.Model):
    """Token used to confirm a newly registered user's email address."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verification_tokens")
    token = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "email_verification_tokens"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):  # pragma: no cover - simple delegation
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=2)
        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    @property
    def is_confirmed(self) -> bool:
        return self.confirmed_at is not None

    def mark_confirmed(self):
        self.confirmed_at = timezone.now()
        self.save(update_fields=["confirmed_at"])


class UserSecurityEvent(models.Model):
    """Keep an audit log of important security related events."""

    EVENT_CHOICES = (
        ("login_success", "Login bem sucedido"),
        ("login_failed", "Login falhou"),
        ("logout", "Logout realizado"),
        ("password_change", "Senha alterada"),
        ("profile_update", "Perfil atualizado"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="security_events")
    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)
    user_agent = models.CharField(max_length=256, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_security_events"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - string formatting
        return f"{self.user.username} - {self.get_event_type_display()} ({self.created_at:%Y-%m-%d %H:%M})"
