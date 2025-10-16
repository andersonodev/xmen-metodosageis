from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Filtro para acessar valores de dicionário no template Django."""
    return dictionary.get(key, [])

@register.filter
def get_team_role(user, team):
    """Filtro para buscar a role de um usuário em uma equipe."""
    if not user or not team:
        return None
    
    from apps.teams.models import TeamMembership
    try:
        membership = TeamMembership.objects.get(
            user=user, 
            team=team, 
            is_active=True
        )
        return membership.get_role_display()
    except TeamMembership.DoesNotExist:
        return None

@register.simple_tag
def user_team_role(user, project):
    """Tag para buscar a role de um usuário na equipe do projeto."""
    if not user or not project or not project.team:
        return None
    
    from apps.teams.models import TeamMembership
    try:
        membership = TeamMembership.objects.get(
            user=user, 
            team=project.team, 
            is_active=True
        )
        return membership.get_role_display()
    except TeamMembership.DoesNotExist:
        return None