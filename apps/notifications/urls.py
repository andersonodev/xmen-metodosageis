from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'notifications'

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    # Web views
    path('', views.notification_list, name='list'),
    path('<int:pk>/read/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    
    # API routes
    path('api/', include(router.urls)),
]