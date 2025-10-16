from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuários."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'bio', 'position', 
            'department', 'availability_hours'
        ]
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs
        
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer para login de usuários."""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Credenciais inválidas.')
            if not user.is_active:
                raise serializers.ValidationError('Conta desativada.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Username e password são obrigatórios.')
        
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer para dados do usuário."""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'role', 'bio', 'avatar', 'position', 
            'department', 'availability_hours', 'is_available',
            'is_active', 'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de perfil."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'bio', 'avatar',
            'position', 'department', 'availability_hours', 'is_available'
        ]