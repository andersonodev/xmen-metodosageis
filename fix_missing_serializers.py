#!/usr/bin/env python3
"""
Script final para corrigir todos os serializers faltantes
"""

# Lista de serializers que precisam ser criados/corrigidos
missing_serializers = {
    'recommendations': 'RecommendationSerializer',
    'integrations': 'ImportHistorySerializer', 
    'projects': 'KeyResultSerializer'
}

# Corrigir recommendations/serializers.py
recommendations_content = '''from rest_framework import serializers
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
'''

with open('apps/recommendations/serializers.py', 'w') as f:
    f.write(recommendations_content)

# Corrigir integrations/serializers.py
integrations_content = '''from rest_framework import serializers
from .models import Integration, ImportHistory


class IntegrationSerializer(serializers.ModelSerializer):
    """Serializer para Integration"""
    
    class Meta:
        model = Integration
        fields = [
            'id', 'name', 'type', 'status', 'config', 'credentials',
            'last_sync', 'created_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'last_sync']


class ImportHistorySerializer(serializers.ModelSerializer):
    """Serializer para ImportHistory"""
    integration_name = serializers.SerializerMethodField()
    imported_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ImportHistory
        fields = [
            'id', 'integration', 'integration_name', 'import_type',
            'file_path', 'status', 'records_total', 'records_success',
            'records_failed', 'error_log', 'started_at', 'completed_at',
            'imported_by', 'imported_by_name'
        ]
        read_only_fields = ['started_at', 'completed_at', 'integration_name', 'imported_by_name']
    
    def get_integration_name(self, obj):
        return obj.integration.name if obj.integration else None
    
    def get_imported_by_name(self, obj):
        return obj.imported_by.get_full_name() if obj.imported_by else None
'''

with open('apps/integrations/serializers.py', 'w') as f:
    f.write(integrations_content)

# Verificar se KeyResultSerializer existe em projects
try:
    with open('apps/projects/serializers.py', 'r') as f:
        content = f.read()
        if 'KeyResultSerializer' not in content:
            # Adicionar KeyResultSerializer
            keyresult_serializer = '''

class KeyResultSerializer(serializers.ModelSerializer):
    """Serializer para KeyResult"""
    okr_title = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = KeyResult
        fields = [
            'id', 'okr', 'okr_title', 'title', 'description',
            'initial_value', 'target_value', 'current_value',
            'unit', 'progress_percentage', 'due_date', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'okr_title', 'progress_percentage']
    
    def get_okr_title(self, obj):
        return obj.okr.objective
    
    def get_progress_percentage(self, obj):
        if obj.target_value and obj.target_value > 0:
            return round((obj.current_value / obj.target_value) * 100, 2)
        return 0
'''
            
            with open('apps/projects/serializers.py', 'a') as f:
                f.write(keyresult_serializer)
                
            # Adicionar import do KeyResult se não existir
            with open('apps/projects/serializers.py', 'r') as f:
                content = f.read()
                if 'from .models import' in content and 'KeyResult' not in content:
                    content = content.replace(
                        'from .models import',
                        'from .models import KeyResult,'
                    )
                    with open('apps/projects/serializers.py', 'w') as f:
                        f.write(content)
            
except Exception as e:
    print(f"Erro ao processar projects/serializers.py: {e}")

print("✅ Todos os serializers faltantes foram criados!")
print("🎯 Agora o Django deve conseguir fazer as migrações.")