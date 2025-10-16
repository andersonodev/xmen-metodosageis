import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserAuthentication:
    """Testes para autenticação de usuários."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.client = APIClient()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'collaborator'
        }
    
    def test_user_registration_success(self):
        """Teste de registro de usuário com sucesso."""
        response = self.client.post(self.register_url, self.user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['username'] == 'testuser'
        
        # Verificar se usuário foi criado no banco
        user = User.objects.get(username='testuser')
        assert user.email == 'test@example.com'
        assert user.role == 'collaborator'
    
    def test_user_registration_password_mismatch(self):
        """Teste de registro com senhas diferentes."""
        self.user_data['password_confirm'] = 'different_password'
        response = self.client.post(self.register_url, self.user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_user_login_success(self):
        """Teste de login com sucesso."""
        # Criar usuário primeiro
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['username'] == 'testuser'
    
    def test_user_login_invalid_credentials(self):
        """Teste de login com credenciais inválidas."""
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserModel:
    """Testes para o modelo User."""
    
    def test_create_user(self):
        """Teste de criação de usuário."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='collaborator'
        )
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == 'collaborator'
        assert user.is_collaborator()
        assert not user.is_leader()
    
    def test_user_full_name_property(self):
        """Teste da propriedade full_name."""
        user = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        
        assert user.full_name == 'Test User'
    
    def test_user_full_name_fallback(self):
        """Teste do fallback da propriedade full_name."""
        user = User.objects.create_user(username='testuser')
        
        assert user.full_name == 'testuser'
    
    def test_user_str_representation(self):
        """Teste da representação string do usuário."""
        user = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            role='leader'
        )
        
        expected = 'Test User (Líder)'
        assert str(user) == expected