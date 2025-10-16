from django.contrib import admin
from .models import MetricSnapshot, ProjectReport, DashboardWidget


@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    """Admin para Snapshots de Métricas."""
    
    list_display = ['metric_type', 'project', 'value', 'period', 'calculated_at']
    list_filter = ['metric_type', 'project', 'calculated_at']
    search_fields = ['metric_type', 'project__name', 'period']
    readonly_fields = ['calculated_at']
    
    fieldsets = (
        ('Métrica', {
            'fields': ('project', 'metric_type', 'value', 'period')
        }),
        ('Dados Adicionais', {
            'fields': ('data',)
        }),
        ('Metadados', {
            'fields': ('calculated_by', 'calculated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectReport)
class ProjectReportAdmin(admin.ModelAdmin):
    """Admin para Relatórios de Projetos."""
    
    list_display = ['title', 'project', 'report_type', 'period_start', 'period_end', 'generated_at']
    list_filter = ['report_type', 'project', 'generated_at', 'period_start']
    search_fields = ['title', 'summary', 'project__name']
    readonly_fields = ['generated_at']
    
    fieldsets = (
        ('Relatório', {
            'fields': ('project', 'report_type', 'title', 'summary')
        }),
        ('Período', {
            'fields': ('period_start', 'period_end')
        }),
        ('Dados', {
            'fields': ('data', 'recommendations')
        }),
        ('Metadados', {
            'fields': ('generated_by', 'generated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    """Admin para Widgets do Dashboard."""
    
    list_display = ['title', 'user', 'widget_type', 'position_x', 'position_y', 'is_visible', 'created_at']
    list_filter = ['widget_type', 'is_visible', 'user', 'created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_visible']
    
    fieldsets = (
        ('Widget', {
            'fields': ('user', 'title', 'widget_type')
        }),
        ('Configuração', {
            'fields': ('config',)
        }),
        ('Posição', {
            'fields': ('position_x', 'position_y', 'width', 'height')
        }),
        ('Visibilidade', {
            'fields': ('is_visible',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
