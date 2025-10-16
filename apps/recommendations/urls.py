from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendationViewSet, recommendation_list, apply_recommendation, dismiss_recommendation, recommendation_detail

router = DefaultRouter()
router.register(r'recommendations', RecommendationViewSet)

app_name = 'recommendations'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Template URLs
    path('', recommendation_list, name='list'),
    path('apply/<int:recommendation_id>/', apply_recommendation, name='apply'),
    path('dismiss/<int:recommendation_id>/', dismiss_recommendation, name='dismiss'),
    path('detail/<int:recommendation_id>/', recommendation_detail, name='detail'),
]