from rest_framework import serializers
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
