from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User


class UserRegistrationForm(UserCreationForm):
    """
    Formulário de registro de usuário com campos personalizados.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite seu primeiro nome'
        }),
        label='Nome'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite seu sobrenome'
        }),
        label='Sobrenome'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'exemplo@empresa.com'
        }),
        label='E-mail'
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome de usuário único'
        }),
        label='Nome de usuário',
        help_text='Será usado para fazer login no sistema'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite uma senha segura'
        }),
        label='Senha'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirme sua senha'
        }),
        label='Confirmar senha'
    )
    
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Função',
        initial='collaborator'
    )
    
    position = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: Desenvolvedor Frontend, Scrum Master...'
        }),
        label='Cargo (opcional)'
    )
    
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: Tecnologia, Produto, Marketing...'
        }),
        label='Departamento (opcional)'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 
                 'password1', 'password2', 'role', 'position', 'department']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nome de usuário já está em uso.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        user.position = self.cleaned_data.get('position', '')
        user.department = self.cleaned_data.get('department', '')
        
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """
    Formulário de login personalizado.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome de usuário ou e-mail',
            'autofocus': True
        }),
        label='Usuário',
        max_length=254
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite sua senha'
        }),
        label='Senha'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        }),
        label='Lembrar de mim'
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Permite login com email ou username
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Tenta autenticar com username processado
            self.user_cache = authenticate(
                self.request, 
                username=username, 
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    'Nome de usuário/e-mail ou senha incorretos.',
                    code='invalid_login'
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    'Esta conta foi desativada.',
                    code='inactive'
                )

        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    """
    Formulário para edição de perfil do usuário.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input'
        }),
        label='Nome'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input'
        }),
        label='Sobrenome'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input'
        }),
        label='E-mail'
    )
    
    position = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input'
        }),
        label='Cargo'
    )
    
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input'
        }),
        label='Departamento'
    )
    
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 4,
            'placeholder': 'Conte um pouco sobre você...'
        }),
        label='Biografia'
    )
    
    availability_hours = forms.IntegerField(
        min_value=1,
        max_value=24,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': '1',
            'max': '24'
        }),
        label='Horas disponíveis por dia'
    )
    
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-input',
            'accept': 'image/*'
        }),
        label='Avatar'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'position', 
                 'department', 'bio', 'availability_hours', 'avatar']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este e-mail já está cadastrado.')
        return email


class PasswordChangeForm(forms.Form):
    """
    Formulário para alteração de senha.
    """
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite sua senha atual'
        }),
        label='Senha atual'
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite a nova senha'
        }),
        label='Nova senha'
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirme a nova senha'
        }),
        label='Confirmar nova senha'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError('Senha atual incorreta.')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError('As senhas não coincidem.')
            
            if len(new_password1) < 8:
                raise ValidationError('A senha deve ter pelo menos 8 caracteres.')

        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
        return self.user