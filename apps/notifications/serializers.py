from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer para Notifications"""
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_name', 'title',
            'message', 'notification_type', 'is_read', 'created_at',
            'read_at', 'action_url', 'metadata'
        ]
        read_only_fields = ['created_at', 'read_at', 'sender_name']
    
    def get_sender_name(self, obj):
        return obj.sender.get_full_name() if obj.sender else 'Sistema'


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer para NotificationPreference"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'notification_type', 'email_enabled',
            'push_enabled', 'in_app_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de notificações"""
    
    class Meta:
        model = Notification
        fields = [
            'recipient', 'sender', 'title', 'message',
            'notification_type', 'action_url', 'metadata'
        ]
    
    def validate_recipient(self, value):
        if value == self.context.get('request').user:
            raise serializers.ValidationError(
                "Você não pode enviar notificação para si mesmo"
            )
        return value


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer para marcar notificações como lidas"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    
    def validate_notification_ids(self, value):
        user = self.context['request'].user
        existing_ids = Notification.objects.filter(
            id__in=value,
            recipient=user
        ).values_list('id', flat=True)
        
        if len(existing_ids) != len(value):
            raise serializers.ValidationError(
                "Algumas notificações não foram encontradas"
            )
        return value


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para lista de notificações"""
    sender_name = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'is_read', 'created_at', 'sender_name', 'time_ago',
            'action_url'
        ]
    
    def get_sender_name(self, obj):
        return obj.sender.get_full_name() if obj.sender else 'Sistema'
    
    def get_time_ago(self, obj):
        from django.utils.timesince import timesince
        return timesince(obj.created_at)


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas de notificações"""
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    notifications_by_type = serializers.DictField()
    recent_notifications = NotificationListSerializer(many=True)


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer para notificações em massa"""
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    notification_type = serializers.ChoiceField(
        choices=Notification.TYPE_CHOICES
    )
    action_url = serializers.URLField(required=False)
    
    def validate_recipient_ids(self, value):
        from apps.accounts.models import User
        existing_ids = User.objects.filter(
            id__in=value
        ).values_list('id', flat=True)
        
        if len(existing_ids) != len(value):
            raise serializers.ValidationError(
                "Alguns usuários não foram encontrados"
            )
        return value


class NotificationPreferenceUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de preferências"""
    
    class Meta:
        model = NotificationPreference
        fields = ['email_enabled', 'push_enabled', 'in_app_enabled']