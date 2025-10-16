from rest_framework import serializers
from .models import Message, ChatRoom


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer para ChatRoom"""
    project_name = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'project', 'project_name', 'is_active',
            'created_at', 'updated_at', 'members_count', 'last_message'
        ]
        read_only_fields = ['created_at', 'updated_at', 'project_name', 'members_count', 'last_message']
    
    def get_project_name(self, obj):
        return obj.project.name
    
    def get_members_count(self, obj):
        return obj.project.team.memberships.filter(is_active=True).count() if obj.project.team else 0
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'content': last_msg.content,
                'author': last_msg.author.get_full_name(),
                'created_at': last_msg.created_at
            }
        return None


class MessageSerializer(serializers.ModelSerializer):
    """Serializer para Message"""
    author_name = serializers.SerializerMethodField()
    author_avatar = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'room', 'author', 'author_name', 'author_avatar',
            'content', 'message_type', 'created_at', 'updated_at',
            'is_edited', 'edited_at', 'time_ago'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'author_name', 'author_avatar',
            'time_ago', 'is_edited', 'edited_at'
        ]
    
    def get_author_name(self, obj):
        return obj.author.get_full_name()
    
    def get_author_avatar(self, obj):
        if obj.author.avatar:
            return obj.author.avatar.url
        return None
    
    def get_time_ago(self, obj):
        from django.utils.timesince import timesince
        return timesince(obj.created_at)


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de mensagens"""
    
    class Meta:
        model = Message
        fields = ['room', 'content', 'message_type']
    
    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Mensagem não pode estar vazia")
        if len(value) > 1000:
            raise serializers.ValidationError("Mensagem muito longa (máximo 1000 caracteres)")
        return value.strip()


class MessageUpdateSerializer(serializers.ModelSerializer):
    """Serializer para edição de mensagens"""
    
    class Meta:
        model = Message
        fields = ['content']
    
    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Mensagem não pode estar vazia")
        if len(value) > 1000:
            raise serializers.ValidationError("Mensagem muito longa (máximo 1000 caracteres)")
        return value.strip()
    
    def update(self, instance, validated_data):
        from django.utils import timezone
        instance.content = validated_data['content']
        instance.is_edited = True
        instance.edited_at = timezone.now()
        instance.save()
        return instance


class MessageListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para lista de mensagens"""
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'author_name', 'content', 'message_type',
            'created_at', 'is_edited'
        ]
    
    def get_author_name(self, obj):
        return obj.author.get_full_name()


class WebSocketMessageSerializer(serializers.Serializer):
    """Serializer para mensagens WebSocket"""
    type = serializers.ChoiceField(choices=[
        'chat_message', 'user_joined', 'user_left', 'typing_start', 'typing_stop'
    ])
    message = serializers.CharField(required=False)
    room_id = serializers.IntegerField(required=False)
    user_id = serializers.IntegerField(required=False)
    timestamp = serializers.DateTimeField(required=False)


class ChatRoomMembersSerializer(serializers.Serializer):
    """Serializer para membros da sala de chat"""
    user_id = serializers.IntegerField()
    user_name = serializers.CharField()
    user_avatar = serializers.URLField(required=False)
    is_online = serializers.BooleanField(default=False)
    last_seen = serializers.DateTimeField(required=False)


class ChatHistorySerializer(serializers.Serializer):
    """Serializer para histórico de chat"""
    room_id = serializers.IntegerField()
    messages = MessageListSerializer(many=True)
    total_messages = serializers.IntegerField()
    has_more = serializers.BooleanField()
    
class ChatStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas de chat"""
    room_id = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    messages_today = serializers.IntegerField()
    active_users = serializers.IntegerField()
    most_active_user = serializers.CharField()