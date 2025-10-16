from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


def home(request):
    """
    Página inicial do Xmen-AgileTeam
    """
    if request.headers.get('Accept', '').startswith('application/json'):
        # Se for uma requisição JSON/API, retornar informações da API
        return JsonResponse({
            'message': 'Bem-vindo ao Xmen-AgileTeam API',
            'version': '1.0.0',
            'description': 'Sistema de gestão ágil para formação de times e projetos',
            'endpoints': {
                'api_docs': '/api/docs/',
                'admin': '/admin/',
                'authentication': '/api/auth/',
                'skills': '/api/skills/',
                'teams': '/api/teams/',
                'projects': '/api/projects/',
                'tasks': '/api/tasks/',
                'dashboards': '/api/dashboards/',
                'notifications': '/api/notifications/',
                'chat': '/api/chat/',
                'recommendations': '/api/recommendations/',
                'integrations': '/api/integrations/'
            },
            'status': 'online'
        })
    
    # Para navegadores, renderizar página HTML
    context = {
        'title': 'Xmen-AgileTeam',
        'description': 'Sistema de gestão ágil para formação de times e projetos',
        'version': '1.0.0'
    }
    return render(request, 'home.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Endpoint de health check para monitoramento
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'xmen-agileteam',
        'version': '1.0.0'
    })