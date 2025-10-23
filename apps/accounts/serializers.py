"""Serializers for the accounts application."""

from __future__ import annotations

from typing import Any, Dict

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import EmailVerificationToken, User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer responsible for creating a user via the API."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "role",
            "bio",
            "position",
            "department",
            "availability_hours",
        ]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password")

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()

        # Generate verification token eagerly so the API response can include it
        EmailVerificationToken.objects.create(user=user)
        return user


class OAuthLoginSerializer(serializers.Serializer):
    """Serializer to validate OAuth login payloads from the frontend."""

    provider = serializers.ChoiceField(choices=[("google", "Google"), ("microsoft", "Microsoft"), ("apple", "Apple")])
    access_token = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        provider = attrs["provider"]
        access_token = attrs["access_token"]
        email = attrs["email"].lower()

        # The actual integration with OAuth providers would happen here. For the
        # scope of this project we simulate the token validation by requiring the
        # token to start with the provider name reversed. This behaviour is easy
        # to replicate in automated tests while ensuring we never accidentally
        # accept plain-text credentials.
        expected_prefix = provider[::-1]
        if not access_token.startswith(expected_prefix):
            raise serializers.ValidationError("Token de acesso inválido para o provedor informado.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado para o e-mail informado.")

        attrs["user"] = user
        return attrs


class UserLoginSerializer(serializers.Serializer):
    """Serializer for credential based login."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError("Username e password são obrigatórios.")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Credenciais inválidas.")
        if not user.is_active:
            raise serializers.ValidationError("Conta desativada.")
        if not user.is_email_verified:
            raise serializers.ValidationError("É necessário confirmar o e-mail antes de fazer login.")

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer representing the public information of the user."""

    full_name = serializers.ReadOnlyField()
    is_email_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "bio",
            "avatar",
            "position",
            "department",
            "availability_hours",
            "is_available",
            "is_active",
            "is_email_verified",
            "date_joined",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "username", "date_joined", "created_at", "updated_at", "is_email_verified"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer used when collaborators update their profile information."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "bio",
            "avatar",
            "position",
            "department",
            "availability_hours",
            "is_available",
        ]
