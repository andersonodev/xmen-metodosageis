from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ChatRoom(models.Model):
    """
    Sala de chat que pode ser associada a diferentes objetos (times, projetos).
    """
    ROOM_TYPE_CHOICES = [
        ('general', 'Geral'),
        ('team', 'Time'),
        ('project', 'Projeto'),
        ('direct', 'Conversa Direta'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='general')
    
    # Relacionamento genérico
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Membros
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ChatMembership',
        related_name='chat_rooms'
    )
    
    # Configurações
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    
    # Metadados
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_chat_rooms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_rooms'
        verbose_name = 'Sala de Chat'
        verbose_name_plural = 'Salas de Chat'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.get_room_type_display()}: {self.name}"
    
    @property
    def last_message(self):
        return self.messages.last()
    
    @property
    def unread_count(self):
        # Implementar contagem de não lidas
        return 0


class ChatMembership(models.Model):
    """
    Relacionamento entre usuário e sala de chat.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('moderator', 'Moderador'),
        ('member', 'Membro'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    
    # Configurações do usuário
    notifications_enabled = models.BooleanField(default=True)
    is_muted = models.BooleanField(default=False)
    
    # Metadados
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_memberships'
        unique_together = ['room', 'user']
    
    def __str__(self):
        return f"{self.user.username} em {self.room.name}"


class Message(models.Model):
    """
    Mensagem no chat.
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Texto'),
        ('image', 'Imagem'),
        ('file', 'Arquivo'),
        ('system', 'Sistema'),
    ]
    
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    
    # Conteúdo
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()
    file_url = models.URLField(blank=True, null=True)
    
    # Resposta/thread
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Estado
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class MessageRead(models.Model):
    """
    Controle de mensagens lidas por usuário.
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_by'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_reads'
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.user.username} leu: {self.message.id}"
