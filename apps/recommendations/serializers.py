from rest_framework import serializers
from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer para Recommendation"""
    content_object_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'content_type', 'object_id', 'content_object_name',
            'type', 'title', 'description', 'confidence', 'metadata',
            'is_active', 'created_at', 'expires_at', 'action_taken'
        ]
        read_only_fields = ['created_at', 'content_object_name']
    
    def get_content_object_name(self, obj):
        if obj.content_object:
            return str(obj.content_object)
        return None


class TeamAllocationSerializer(serializers.Serializer):
    """Serializer para recomendação de alocação de time"""
    user_id = serializers.IntegerField()
    user_name = serializers.CharField()
    skills = serializers.ListField(child=serializers.CharField())
    compatibility_score = serializers.FloatField()
    role_suggestion = serializers.CharField()


class RiskAnalysisSerializer(serializers.Serializer):
    """Serializer para análise de risco"""
    risk_type = serializers.CharField()
    probability = serializers.FloatField()
    impact = serializers.CharField()
    description = serializers.CharField()
    mitigation_suggestions = serializers.ListField(child=serializers.CharField())
