from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, SprintViewSet, OKRViewSet, KeyResultViewSet,
    project_list, project_detail, project_create, project_edit
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
    
    # API endpoints
    path('', include(router.urls)),
]