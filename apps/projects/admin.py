from django.contrib import admin
from .models import ProjectTemplate, ProjectTemplateSkill, Project, Sprint, OKR, KeyResult


class ProjectTemplateSkillInline(admin.TabularInline):
    """Inline para skills do template."""
    model = ProjectTemplateSkill
    extra = 1


class KeyResultInline(admin.TabularInline):
    """Inline para resultados-chave do OKR."""
    model = KeyResult
    extra = 1
    readonly_fields = ['progress_percentage']


class SprintInline(admin.TabularInline):
    """Inline para sprints do projeto."""
    model = Sprint
    extra = 0
    readonly_fields = ['created_at']
    fields = ['name', 'status', 'start_date', 'end_date', 'planned_points', 'completed_points']


@admin.register(ProjectTemplate)
class ProjectTemplateAdmin(admin.ModelAdmin):
    """Admin para Templates de Projetos."""
    
    list_display = ['name', 'default_duration_days', 'default_team_size', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    list_editable = ['is_active']
    inlines = [ProjectTemplateSkillInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description')
        }),
        ('Configurações Padrão', {
            'fields': ('default_duration_days', 'default_team_size', 'is_active')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin para Projetos."""
    
    list_display = ['name', 'status', 'priority', 'team', 'progress_percentage', 'start_date', 'end_date']
    list_filter = ['status', 'priority', 'team', 'start_date', 'created_at']
    search_fields = ['name', 'description', 'team__name', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'progress_percentage']
    list_editable = ['status', 'priority']
    inlines = [SprintInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'template')
        }),
        ('Status e Prioridade', {
            'fields': ('status', 'priority')
        }),
        ('Relacionamentos', {
            'fields': ('team', 'created_by')
        }),
        ('Datas', {
            'fields': ('start_date', 'end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('Estimativas', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('Estatísticas', {
            'fields': ('progress_percentage',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def progress_percentage(self, obj):
        return f"{obj.progress_percentage}%"
    progress_percentage.short_description = 'Progresso'


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    """Admin para Sprints."""
    
    list_display = ['name', 'project', 'status', 'start_date', 'end_date', 'planned_points', 'completed_points', 'completion_rate']
    list_filter = ['status', 'project', 'start_date', 'created_at']
    search_fields = ['name', 'goal', 'project__name']
    readonly_fields = ['created_at', 'completion_rate']
    list_editable = ['status']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('project', 'name', 'goal')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Datas', {
            'fields': ('start_date', 'end_date')
        }),
        ('Métricas', {
            'fields': ('planned_points', 'completed_points', 'completion_rate')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def completion_rate(self, obj):
        if obj.planned_points == 0:
            return "0%"
        rate = (obj.completed_points / obj.planned_points) * 100
        return f"{rate:.1f}%"
    completion_rate.short_description = 'Taxa Conclusão'


@admin.register(OKR)
class OKRAdmin(admin.ModelAdmin):
    """Admin para OKRs."""
    
    list_display = ['objective', 'project', 'quarter', 'year', 'progress_percentage', 'key_results_count']
    list_filter = ['year', 'quarter', 'project', 'created_at']
    search_fields = ['objective', 'description', 'project__name']
    readonly_fields = ['created_at', 'updated_at', 'key_results_count']
    list_editable = ['progress_percentage']
    inlines = [KeyResultInline]
    
    fieldsets = (
        ('Objetivo', {
            'fields': ('project', 'objective', 'description')
        }),
        ('Período', {
            'fields': ('quarter', 'year')
        }),
        ('Progresso', {
            'fields': ('progress_percentage',)
        }),
        ('Estatísticas', {
            'fields': ('key_results_count',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def key_results_count(self, obj):
        return obj.key_results.count()
    key_results_count.short_description = 'Qtd Resultados-Chave'


@admin.register(KeyResult)
class KeyResultAdmin(admin.ModelAdmin):
    """Admin para Resultados-Chave."""
    
    list_display = ['description', 'okr', 'current_value', 'target_value', 'unit', 'progress_percentage']
    list_filter = ['okr__project', 'okr__year', 'okr__quarter']
    search_fields = ['description', 'okr__objective']
    readonly_fields = ['created_at', 'updated_at', 'progress_percentage']
    
    fieldsets = (
        ('Resultado-Chave', {
            'fields': ('okr', 'description')
        }),
        ('Métricas', {
            'fields': ('target_value', 'current_value', 'unit', 'progress_percentage')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def progress_percentage(self, obj):
        return f"{obj.progress_percentage}%"
    progress_percentage.short_description = 'Progresso'
