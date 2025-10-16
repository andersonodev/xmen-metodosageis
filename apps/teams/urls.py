from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'teams'

# API routes
router = DefaultRouter()
router.register(r'teams', views.TeamViewSet)
router.register(r'memberships', views.TeamMembershipViewSet)
router.register(r'invitations', views.TeamInvitationViewSet)

urlpatterns = [
    # Web views
    path('', views.team_list, name='list'),
    path('<int:pk>/', views.team_detail, name='detail'),
    path('create/', views.team_create, name='create'),
    path('<int:pk>/edit/', views.team_edit, name='edit'),
    path('<int:pk>/members/', views.ajax_team_members, name='ajax-members'),
    
    # API routes
    path('api/', include(router.urls)),
    path('api/users/', views.UserListAPIView.as_view(), name='api-users-list'),
    path('api/teams/<int:team_id>/join/', views.JoinTeamAPIView.as_view(), name='api-join-team'),
    path('api/teams/<int:team_id>/leave/', views.LeaveTeamAPIView.as_view(), name='api-leave-team'),
    path('api/invitations/<int:invitation_id>/accept/', views.AcceptInvitationAPIView.as_view(), name='api-accept-invitation'),
    path('api/invitations/<int:invitation_id>/decline/', views.DeclineInvitationAPIView.as_view(), name='api-decline-invitation'),
]