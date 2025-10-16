from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MetricSnapshotViewSet, ProjectReportViewSet, DashboardWidgetViewSet, main_dashboard

app_name = 'dashboards'

router = DefaultRouter()
router.register(r'api/metrics', MetricSnapshotViewSet)
router.register(r'api/reports', ProjectReportViewSet)
router.register(r'api/widgets', DashboardWidgetViewSet)

urlpatterns = [
    # Web templates
    path('', main_dashboard, name='main'),
    
    # API endpoints
    path('', include(router.urls)),
]