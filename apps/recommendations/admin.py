from django.contrib import admin
from .models import Recommendation, AIModel


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    """Admin para Recomendações da IA."""
    
    list_display = ['title', 'type', 'confidence', 'score', 'is_active', 'is_applied', 'user_feedback', 'created_at']
    list_filter = ['type', 'confidence', 'is_active', 'is_applied', 'user_feedback', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'applied_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Recomendação', {
            'fields': ('type', 'title', 'description')
        }),
        ('Relacionamento', {
            'fields': ('content_type', 'object_id')
        }),
        ('Dados da IA', {
            'fields': ('confidence', 'score', 'data')
        }),
        ('Status', {
            'fields': ('is_active', 'is_applied', 'applied_at', 'applied_by')
        }),
        ('Feedback', {
            'fields': ('user_feedback', 'feedback_comment')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_applied', 'mark_as_not_applied', 'activate_recommendations']
    
    def mark_as_applied(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_applied=True, applied_at=timezone.now(), applied_by=request.user)
        self.message_user(request, f"{queryset.count()} recomendações marcadas como aplicadas.")
    mark_as_applied.short_description = "Marcar como aplicadas"
    
    def mark_as_not_applied(self, request, queryset):
        queryset.update(is_applied=False, applied_at=None, applied_by=None)
        self.message_user(request, f"{queryset.count()} recomendações marcadas como não aplicadas.")
    mark_as_not_applied.short_description = "Marcar como não aplicadas"
    
    def activate_recommendations(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} recomendações ativadas.")
    activate_recommendations.short_description = "Ativar recomendações"


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    """Admin para Modelos de IA."""
    
    list_display = ['name', 'version', 'is_active', 'accuracy_score', 'last_trained_at', 'created_at']
    list_filter = ['is_active', 'last_trained_at', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Modelo', {
            'fields': ('name', 'description', 'version')
        }),
        ('Configurações', {
            'fields': ('config', 'is_active')
        }),
        ('Performance', {
            'fields': ('accuracy_score', 'last_trained_at')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
