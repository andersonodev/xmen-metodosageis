from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    # API Views
    UserRegistrationView,
    login_view,
    OAuthLoginView,
    UserProfileView,
    UserListView,
    UserDetailView,
    EmailVerificationView,
    CollaboratorSearchView,
    HRIntegrationView,
    # Template Views
    RegisterView,
    LoginView,
    logout_view,
    profile_view,
    profile_detail_view,
    collaborator_search_page,
    bulk_import_view,
    user_management_view,
    special_admin_view
)

from .profile_views import (
    admin_dashboard,
    leader_dashboard, 
    collaborator_dashboard,
    create_ai_team
)

app_name = 'accounts'

urlpatterns = [
    # API Authentication endpoints
    path('api/auth/register/', UserRegistrationView.as_view(), name='api_register'),
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', login_view, name='api_login'),
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/oauth/', OAuthLoginView.as_view(), name='api_oauth_login'),
    path('api/auth/verify-email/', EmailVerificationView.as_view(), name='api_verify_email'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API User endpoints
    path('api/users/', UserListView.as_view(), name='api_user_list'),
    path('api/users/<int:pk>/', UserDetailView.as_view(), name='api_user_detail'),
    path('api/profile/', UserProfileView.as_view(), name='api_user_profile'),
    path('api/collaborators/search/', CollaboratorSearchView.as_view(), name='api_collaborator_search'),
    path('api/hr/sync/', HRIntegrationView.as_view(), name='api_hr_sync'),

    # Web Template endpoints
    path('login/', LoginView.as_view(), name='web_login'),
    path('register/', RegisterView.as_view(), name='web_register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/<int:pk>/', profile_detail_view, name='profile_detail'),
    path('profile/full/', profile_detail_view, name='profile_self_detail'),
    path('collaborators/search/', collaborator_search_page, name='search_collaborators'),
    path('import/', bulk_import_view, name='bulk_import'),
    path('users/manage/', user_management_view, name='user_management'),
    
    # Role-based Dashboard endpoints - REMOVIDO admin-dashboard da URL pública
    path('leader-dashboard/', leader_dashboard, name='leader_dashboard'),
    path('collaborator-dashboard/', collaborator_dashboard, name='collaborator_dashboard'),
    
    # Rota especial e oculta para admin (só funciona com token)
    path('xmen-admin-special/', special_admin_view, name='special_admin'),
    
    # AI endpoints
    path('create-ai-team/', create_ai_team, name='create_ai_team'),
]