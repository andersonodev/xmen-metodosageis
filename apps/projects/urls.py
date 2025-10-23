from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    SprintViewSet,
    OKRViewSet,
    KeyResultViewSet,
    project_list,
    project_detail,
    project_create,
    project_edit,
    active_projects_view,
    report_generator,
)

app_name = 'projects'

router = DefaultRouter()
router.register(r'api/projects', ProjectViewSet)
router.register(r'api/sprints', SprintViewSet)
router.register(r'api/okrs', OKRViewSet)
router.register(r'api/key-results', KeyResultViewSet)

urlpatterns = [
    # Web templates
    path('', project_list, name='list'),
    path('create/', project_create, name='create'),
    path('<int:pk>/', project_detail, name='detail'),
    path('<int:pk>/edit/', project_edit, name='edit'),
    path('ativos/', active_projects_view, name='active'),
    path('relatorios/', report_generator, name='report_generator'),
    
    # API endpoints
    path('', include(router.urls)),
]