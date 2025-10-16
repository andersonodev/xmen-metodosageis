from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema

from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer,
    UserProfileUpdateSerializer
)
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm


class UserRegistrationView(generics.CreateAPIView):
    """
    View para registro de novos usuários.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        tags=['Authentication'],
        summary='Registrar novo usuário',
        description='Cria um novo usuário no sistema'
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Login de usuário',
    description='Autentica usuário e retorna tokens JWT'
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    View para login de usuários.
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View para visualizar e atualizar perfil do usuário logado.
    """
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        tags=['Users'],
        summary='Obter perfil do usuário',
        description='Retorna dados do perfil do usuário logado'
    )
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(self.get_object())
        return Response(serializer.data)
    
    @extend_schema(
        tags=['Users'],
        summary='Atualizar perfil',
        description='Atualiza dados do perfil do usuário logado'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class UserListView(generics.ListAPIView):
    """
    View para listar usuários (apenas para líderes).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Apenas líderes podem ver todos os usuários
        if self.request.user.is_leader() or self.request.user.is_staff:
            return User.objects.filter(is_active=True)
        return User.objects.filter(id=self.request.user.id)
    
    @extend_schema(
        tags=['Users'],
        summary='Listar usuários',
        description='Lista todos os usuários (apenas para líderes)'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserDetailView(generics.RetrieveAPIView):
    """
    View para visualizar detalhes de um usuário específico.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        tags=['Users'],
        summary='Detalhes do usuário',
        description='Retorna detalhes de um usuário específico'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ===============================
# VIEWS PARA TEMPLATES (WEB UI)
# ===============================

@method_decorator([csrf_protect, never_cache], name='dispatch')
class RegisterView(CreateView):
    """
    View para registro de novos usuários via template.
    """
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:web_login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            'Cadastro realizado com sucesso! Faça login para continuar.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Erro no cadastro. Verifique os dados e tente novamente.'
        )
        return super().form_invalid(form)


@method_decorator([csrf_protect, never_cache], name='dispatch')
class LoginView(FormView):
    """
    View para login de usuários via template.
    """
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        
        # Define sessão permanente se "lembrar de mim" estiver marcado
        if form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(1209600)  # 2 semanas
        else:
            self.request.session.set_expiry(0)  # Expira ao fechar o browser
        
        messages.success(
            self.request,
            f'Bem-vindo(a), {user.first_name or user.username}!'
        )
        
        # Redireciona para next se fornecido, senão redireciona para dashboard
        next_url = self.request.GET.get('next')
        if next_url:
            return redirect(next_url)
        
        # Redireciona para o dashboard principal
        return redirect('dashboards:main')
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Credenciais inválidas. Verifique seus dados e tente novamente.'
        )
        return super().form_invalid(form)


@login_required
def logout_view(request):
    """
    View para logout do usuário.
    """
    user_name = request.user.first_name or request.user.username
    logout(request)
    messages.success(request, f'Até logo, {user_name}!')
    return redirect('accounts:web_login')


@login_required
def profile_view(request):
    """
    View para visualizar e editar perfil do usuário.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Erro ao atualizar perfil. Verifique os dados.')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'accounts/profile.html', context)


def home_view(request):
    """
    View da página inicial - redireciona para dashboard apropriado se logado.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:web_login')
    else:
        # Redireciona para o dashboard principal
        return redirect('dashboards:main')


@login_required
def special_admin_view(request):
    """
    View especial do admin que só pode ser acessada com token especial.
    Esta é uma rota oculta que substitui admin-dashboard.
    """
    from django.http import Http404
    from .profile_views import admin_dashboard
    
    # Verifica se o usuário é admin
    if not request.user.is_superuser:
        raise Http404("Página não encontrada")
    
    # Verifica se tem o token especial na sessão ou como parâmetro
    special_token = request.session.get('special_admin_token') or request.GET.get('token')
    
    if special_token == 'admin_access_xmen_2024':
        # Define o token na sessão para futuras requisições
        request.session['special_admin_token'] = 'admin_access_xmen_2024'
        return admin_dashboard(request)
    
    raise Http404("Página não encontrada")
