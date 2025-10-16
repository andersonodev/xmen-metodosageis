from django.contrib import admin
from .models import ChatRoom, ChatMembership, Message, MessageRead


class MessageInline(admin.TabularInline):
    """Inline para mensagens da sala de chat."""
    model = Message
    extra = 0
    readonly_fields = ['created_at', 'is_edited', 'edited_at']
    fields = ['sender', 'message_type', 'content', 'created_at']


class ChatMembershipInline(admin.TabularInline):
    """Inline para membros da sala de chat."""
    model = ChatMembership
    extra = 0
    readonly_fields = ['joined_at', 'last_read_at']


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    """Admin para Salas de Chat."""
    
    list_display = ['name', 'room_type', 'is_active', 'is_public', 'messages_count', 'members_count', 'created_at']
    list_filter = ['room_type', 'is_active', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'messages_count', 'members_count']
    list_editable = ['is_active']
    inlines = [ChatMembershipInline, MessageInline]
    
    fieldsets = (
        ('Sala de Chat', {
            'fields': ('name', 'description', 'room_type')
        }),
        ('Configurações', {
            'fields': ('is_active', 'is_public')
        }),
        ('Relacionamento', {
            'fields': ('content_type', 'object_id', 'created_by'),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': ('messages_count', 'members_count'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def messages_count(self, obj):
        return obj.messages.count()
    messages_count.short_description = 'Qtd Mensagens'
    
    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = 'Qtd Membros'


@admin.register(ChatMembership)
class ChatMembershipAdmin(admin.ModelAdmin):
    """Admin para Membros das Salas de Chat."""
    
    list_display = ['user', 'room', 'role', 'notifications_enabled', 'is_muted', 'joined_at']
    list_filter = ['role', 'notifications_enabled', 'is_muted', 'joined_at']
    search_fields = ['user__username', 'room__name']
    readonly_fields = ['joined_at', 'last_read_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin para Mensagens do Chat."""
    
    list_display = ['sender', 'room', 'message_type', 'content_preview', 'is_edited', 'created_at']
    list_filter = ['message_type', 'room', 'is_edited', 'created_at']
    search_fields = ['content', 'sender__username', 'room__name']
    readonly_fields = ['created_at', 'edited_at', 'is_edited']
    
    fieldsets = (
        ('Mensagem', {
            'fields': ('room', 'sender', 'message_type', 'content')
        }),
        ('Arquivo/URL', {
            'fields': ('file_url',)
        }),
        ('Resposta', {
            'fields': ('reply_to',)
        }),
        ('Status', {
            'fields': ('is_edited', 'edited_at')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Conteúdo'


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    """Admin para Controle de Leitura das Mensagens."""
    
    list_display = ['user', 'message', 'read_at']
    list_filter = ['read_at', 'user']
    search_fields = ['user__username', 'message__content']
    readonly_fields = ['read_at']
    
    fieldsets = (
        ('Leitura', {
            'fields': ('message', 'user')
        }),
        ('Metadados', {
            'fields': ('read_at',),
            'classes': ('collapse',)
        }),
    )
