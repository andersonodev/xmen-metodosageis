from django.contrib import admin
from .models import SkillCategory, Skill, UserSkill, SkillRequirement


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    """Admin para Categorias de Habilidades."""
    
    list_display = ['name', 'icon', 'skills_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'icon')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def skills_count(self, obj):
        return obj.skills.count()
    skills_count.short_description = 'Qtd Habilidades'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Admin para Habilidades."""
    
    list_display = ['name', 'category', 'is_active', 'users_count', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'category')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def users_count(self, obj):
        return obj.user_skills.count()
    users_count.short_description = 'Qtd Usuários'


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    """Admin para Habilidades dos Usuários."""
    
    list_display = ['user', 'skill', 'level', 'level_display', 'is_validated', 'validated_by', 'created_at']
    list_filter = ['level', 'is_validated', 'skill__category', 'created_at']
    search_fields = ['user__username', 'user__email', 'skill__name']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['level', 'is_validated']
    
    fieldsets = (
        ('Relacionamento', {
            'fields': ('user', 'skill', 'level')
        }),
        ('Validação', {
            'fields': ('is_validated', 'validated_by', 'validated_at')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def level_display(self, obj):
        return obj.get_level_display()
    level_display.short_description = 'Nível'


@admin.register(SkillRequirement)
class SkillRequirementAdmin(admin.ModelAdmin):
    """Admin para Requisitos de Habilidades."""
    
    list_display = ['skill', 'min_level', 'is_mandatory', 'content_type', 'object_id', 'created_at']
    list_filter = ['min_level', 'is_mandatory', 'content_type', 'created_at']
    search_fields = ['skill__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Requisito', {
            'fields': ('skill', 'min_level', 'is_mandatory')
        }),
        ('Relacionamento', {
            'fields': ('content_type', 'object_id')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
