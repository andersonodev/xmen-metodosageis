from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'tasks'

router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet)
router.register(r'columns', views.ColumnViewSet)
router.register(r'comments', views.TaskCommentViewSet)

urlpatterns = [
    # Web views
    path('', views.task_board, name='board'),
    path('project/<int:project_id>/', views.task_board, name='project_board'),
    path('list/', views.task_list, name='list'),
    path('<int:pk>/', views.task_detail, name='detail'),
    path('create/', views.task_create, name='create'),
    path('project/<int:project_id>/create/', views.task_create, name='project_create'),
    
    # AJAX endpoints
    path('update-column/', views.update_task_column, name='update_column'),
    path('create-column/', views.create_column, name='create_column'),
    path('column/<int:column_id>/update/', views.update_column, name='update_column_detail'),
    path('column/<int:column_id>/delete/', views.delete_column, name='delete_column'),
    path('create-quick/', views.create_task_quick, name='create_quick'),
    path('<int:pk>/modal/', views.task_detail_modal, name='detail_modal'),
    path('<int:pk>/update/', views.update_task, name='update_task'),
    path('<int:pk>/delete/', views.delete_task, name='delete_task'),
    path('<int:task_id>/comment/', views.add_comment, name='add_comment'),
    
    # API routes
    path('api/', include(router.urls)),
]