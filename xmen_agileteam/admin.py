from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin


# Configurações básicas do admin
admin.site.site_header = "Xmen-AgileTeam Admin"
admin.site.site_title = "Xmen-AgileTeam"
admin.site.index_title = "Painel de Administração"


class CustomGroupAdmin(GroupAdmin):
    """Admin customizado para grupos."""
    list_display = ['name', 'users_count']
    
    def users_count(self, obj):
        return obj.user_set.count()
    users_count.short_description = 'Qtd Usuários'


# Re-registrar o GroupAdmin customizado
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)