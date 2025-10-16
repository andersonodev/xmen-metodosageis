"""
URL configuration for xmen_agileteam project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import views
from apps.accounts.views import home_view

urlpatterns = [
    # Home page
    path('', home_view, name='home'),
    path('health/', views.health_check, name='health_check'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication & User Management (Web + API)
    path('accounts/', include('apps.accounts.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Web Views
    path('dashboard/', include('apps.dashboards.urls')),
    path('projects/', include('apps.projects.urls')),
    path('teams/', include('apps.teams.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('skills/', include('apps.skills.urls')),
    path('chat/', include('apps.chat.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('integrations/', include('apps.integrations.urls')),
    path('api/recommendations/', include('apps.recommendations.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
