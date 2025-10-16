from django.contrib import admin
from .models import Team, TeamMembership, TeamInvitation


class TeamMembershipInline(admin.TabularInline):
    """Inline para membros do time."""
    model = TeamMembership
    extra = 1
    fields = ['user', 'role', 'is_active', 'is_lead', 'allocation_percentage']
    readonly_fields = ['joined_at']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin para Times."""
    
    list_display = ['name', 'member_count', 'max_members', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at', 'created_by']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'member_count']
    list_editable = ['is_active']
    inlines = [TeamMembershipInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Configurações', {
            'fields': ('max_members', 'is_active')
        }),
        ('Estatísticas', {
            'fields': ('member_count',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = 'Qtd Membros'


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    """Admin para Membros dos Times."""
    
    list_display = ['user', 'team', 'role', 'is_active', 'is_lead', 'allocation_percentage', 'joined_at']
    list_filter = ['role', 'is_active', 'is_lead', 'team', 'joined_at']
    search_fields = ['user__username', 'user__email', 'team__name']
    readonly_fields = ['joined_at']
    list_editable = ['is_active', 'is_lead', 'allocation_percentage']
    
    fieldsets = (
        ('Relacionamento', {
            'fields': ('team', 'user', 'role')
        }),
        ('Status', {
            'fields': ('is_active', 'is_lead', 'allocation_percentage')
        }),
        ('Datas', {
            'fields': ('joined_at', 'left_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    """Admin para Convites de Times."""
    
    list_display = ['invited_user', 'team', 'proposed_role', 'status', 'invited_by', 'created_at', 'expires_at']
    list_filter = ['status', 'proposed_role', 'created_at', 'expires_at']
    search_fields = ['invited_user__username', 'team__name', 'invited_by__username']
    readonly_fields = ['created_at', 'responded_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Convite', {
            'fields': ('team', 'invited_user', 'invited_by', 'proposed_role')
        }),
        ('Mensagem', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('status', 'expires_at')
        }),
        ('Datas', {
            'fields': ('created_at', 'responded_at'),
            'classes': ('collapse',)
        }),
    )
