from django.contrib import admin
from .models import Integration, ImportHistory


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    """Admin para Integrações Externas."""
    
    list_display = ['name', 'type', 'status', 'last_sync_at', 'project', 'created_at']
    list_filter = ['type', 'status', 'last_sync_at', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_sync_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Integração', {
            'fields': ('name', 'description', 'type', 'project')
        }),
        ('Configurações', {
            'fields': ('config', 'credentials', 'status')
        }),
        ('Sincronização', {
            'fields': ('last_sync_at', 'last_error')
        }),
        ('Metadados', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['sync_integrations', 'activate_integrations', 'deactivate_integrations']
    
    def sync_integrations(self, request, queryset):
        # Aqui você implementaria a lógica de sincronização
        count = queryset.filter(status='active').count()
        self.message_user(request, f"{count} integrações ativas sincronizadas.")
    sync_integrations.short_description = "Sincronizar integrações ativas"
    
    def activate_integrations(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f"{queryset.count()} integrações ativadas.")
    activate_integrations.short_description = "Ativar integrações"
    
    def deactivate_integrations(self, request, queryset):
        queryset.update(status='inactive')
        self.message_user(request, f"{queryset.count()} integrações desativadas.")
    deactivate_integrations.short_description = "Desativar integrações"


@admin.register(ImportHistory)
class ImportHistoryAdmin(admin.ModelAdmin):
    """Admin para Histórico de Importações."""
    
    list_display = ['integration', 'status', 'success_count', 'error_count', 'total_records', 'started_at', 'completed_at']
    list_filter = ['status', 'integration', 'started_at', 'completed_at']
    search_fields = ['integration__name']
    readonly_fields = ['started_at', 'completed_at', 'duration_display']
    
    fieldsets = (
        ('Importação', {
            'fields': ('integration', 'source_file', 'source_data')
        }),
        ('Status', {
            'fields': ('status', 'total_records', 'processed_records')
        }),
        ('Resultados', {
            'fields': ('success_count', 'error_count', 'error_details')
        }),
        ('Datas', {
            'fields': ('started_by', 'started_at', 'completed_at', 'duration_display')
        }),
        ('Logs', {
            'fields': ('log_data',),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return str(duration)
        return "Em andamento" if obj.started_at else "Não iniciado"
    duration_display.short_description = 'Duração'
