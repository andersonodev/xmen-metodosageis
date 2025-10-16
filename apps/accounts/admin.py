from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin customizado para o modelo User."""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'role', 'position', 'is_available', 'is_active', 'date_joined'
    ]
    list_filter = ['role', 'is_available', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'position']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Profissionais', {
            'fields': ('role', 'bio', 'avatar', 'position', 'department')
        }),
        ('Disponibilidade', {
            'fields': ('availability_hours', 'is_available')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações Profissionais', {
            'fields': ('role', 'position', 'department', 'availability_hours')
        }),
    )
