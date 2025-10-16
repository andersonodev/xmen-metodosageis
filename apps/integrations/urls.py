from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'integrations'

router = DefaultRouter()
router.register(r'integrations', views.IntegrationViewSet)
router.register(r'history', views.ImportHistoryViewSet)

urlpatterns = [
    # Web views
    path('', views.integration_list, name='list'),
    path('<int:pk>/', views.integration_detail, name='detail'),
    path('<int:pk>/toggle/', views.toggle_integration, name='toggle'),
    path('<int:pk>/delete/', views.delete_integration, name='delete'),
    path('<int:pk>/sync/', views.sync_integration, name='sync'),
    path('<int:pk>/test/', views.test_integration, name='test'),
    path('<int:pk>/logs/', views.get_integration_logs, name='logs'),
    
    # API routes
    path('api/', include(router.urls)),
]