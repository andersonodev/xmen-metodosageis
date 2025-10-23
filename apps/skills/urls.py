from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'skills'

router = DefaultRouter()
router.register(r'categories', views.SkillCategoryViewSet)
router.register(r'skills', views.SkillViewSet)
router.register(r'user-skills', views.UserSkillViewSet)

urlpatterns = [
    # Web views
    path('', views.skill_list, name='list'),
    path('create/', views.skill_create, name='create'),
    path('edit/', views.edit_competencies, name='edit'),
    path('<int:pk>/', views.skill_detail, name='detail'),
    path('<int:skill_id>/add/', views.add_skill, name='add'),
    path('add-user-skill/', views.add_user_skill, name='add_user_skill'),
    path('<int:skill_id>/remove/', views.remove_skill, name='remove'),
    path('<int:skill_id>/update-level/', views.update_skill_level, name='update_level'),
    
    # API routes
    path('api/', include(router.urls)),
]