"""Views for the accounts application."""

from __future__ import annotations

import logging
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, FormView
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema

from apps.projects.models import Project
from apps.skills.models import Skill, UserSkill
from apps.teams.models import TeamMembership

from .forms import (
    CollaboratorImportForm,
    UserLoginForm,
    UserProfileForm,
    UserRegistrationForm,
    UserRoleForm,
)
from .models import EmailVerificationToken, User, UserSecurityEvent
from .serializers import (
    OAuthLoginSerializer,
    UserLoginSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


def _record_security_event(request: HttpRequest, user: User, event_type: str) -> None:
    """Persist a :class:`UserSecurityEvent` with contextual information."""

    UserSecurityEvent.objects.create(
        user=user,
        event_type=event_type,
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:256],
        ip_address=request.META.get("REMOTE_ADDR"),
    )


class UserRegistrationView(generics.CreateAPIView):
    """API endpoint to register a new user."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Registrar novo usuário",
        description="Cria um novo usuário no sistema e envia token de verificação de e-mail.",
    )
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = user.verification_tokens.latest("created_at")

        logger.info("Novo usuário cadastrado. Token de verificação: %s", token.token)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "verification_token": token.token,
                "tokens": {"refresh": str(refresh), "access": str(refresh.access_token)},
            },
            status=status.HTTP_201_CREATED,
        )


class EmailVerificationView(APIView):
    """Confirm the e-mail of a user using the generated token."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["Authentication"], summary="Confirmar e-mail do usuário")
    def post(self, request: HttpRequest) -> Response:
        token_value = request.data.get("token")
        if not token_value:
            return Response({"detail": "Token é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        token = get_object_or_404(EmailVerificationToken, token=token_value)
        if token.is_confirmed:
            return Response({"detail": "Token já utilizado."}, status=status.HTTP_200_OK)
        if token.is_expired:
            return Response({"detail": "Token expirado."}, status=status.HTTP_400_BAD_REQUEST)

        token.mark_confirmed()
        return Response({"detail": "E-mail confirmado com sucesso."}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Authentication"],
    summary="Login de usuário",
    description="Autentica usuário e retorna tokens JWT",
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request: HttpRequest) -> Response:
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data["user"]
    login(request, user)
    refresh = RefreshToken.for_user(user)

    _record_security_event(request, user, "login_success")

    return Response(
        {
            "user": UserSerializer(user).data,
            "tokens": {"refresh": str(refresh), "access": str(refresh.access_token)},
        }
    )


class OAuthLoginView(APIView):
    """Authenticate a user using a third-party OAuth provider token."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["Authentication"], summary="Login via OAuth")
    def post(self, request: HttpRequest) -> Response:
        serializer = OAuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        if not user.is_email_verified:
            return Response(
                {"detail": "Confirme seu e-mail antes de utilizar o login social."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_token = RefreshToken.for_user(user)

        _record_security_event(request, user, "login_success")

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {"refresh": str(user_token), "access": str(user_token.access_token)},
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Allow the authenticated user to retrieve or update their profile."""

    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user

    @extend_schema(tags=["Users"], summary="Obter perfil do usuário")
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        serializer = UserSerializer(self.get_object())
        return Response(serializer.data)

    @extend_schema(tags=["Users"], summary="Atualizar perfil")
    def patch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        response = super().patch(request, *args, **kwargs)
        _record_security_event(request, request.user, "profile_update")
        return response


class UserListView(generics.ListAPIView):
    """List users available to the requester."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_leader() or self.request.user.is_staff:
            return User.objects.filter(is_active=True)
        return User.objects.filter(id=self.request.user.id)


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class CollaboratorSearchView(APIView):
    """Search collaborators based on the skills they own."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Users"], summary="Buscar colaboradores por competência")
    def get(self, request: HttpRequest) -> Response:
        skills = request.query_params.getlist("skill")
        minimum_level = int(request.query_params.get("min_level", 3))

        user_skills_qs = UserSkill.objects.filter(level__gte=minimum_level).select_related("skill", "user")
        if skills:
            user_skills_qs = user_skills_qs.filter(skill__name__in=skills)

        collaborator_ids = user_skills_qs.values_list("user_id", flat=True).distinct()
        collaborators = User.objects.filter(id__in=collaborator_ids)

        skills_by_user: Dict[int, list[Dict[str, Any]]] = {}
        for user_skill in user_skills_qs:
            skills_by_user.setdefault(user_skill.user_id, []).append(
                {"skill": user_skill.skill.name, "level": user_skill.level}
            )

        payload = [
            {
                "id": user.id,
                "full_name": user.full_name,
                "role": user.role,
                "email": user.email,
                "skills": skills_by_user.get(user.id, []),
            }
            for user in collaborators
        ]

        return Response(payload)


class HRIntegrationView(APIView):
    """Expose collaborator data for HR synchronisation."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Integrations"], summary="Sincronizar dados para RH")
    def get(self, request: HttpRequest) -> Response:
        collaborators = (
            User.objects.filter(is_active=True)
            .prefetch_related("user_skills__skill")
            .order_by("first_name", "last_name")
        )

        payload = []
        for collaborator in collaborators:
            active_projects = Project.objects.filter(
                Q(team__memberships__user=collaborator) | Q(created_by=collaborator)
            ).values("name", "status")

            payload.append(
                {
                    "username": collaborator.username,
                    "full_name": collaborator.full_name,
                    "email": collaborator.email,
                    "role": collaborator.role,
                    "skills": [
                        {"name": user_skill.skill.name, "level": user_skill.level}
                        for user_skill in collaborator.user_skills.all()
                    ],
                    "projects": list(active_projects),
                }
            )

        return Response(payload)


# ===============================
# VIEWS PARA TEMPLATES (WEB UI)
# ===============================


@method_decorator([csrf_protect, never_cache], name="dispatch")
class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:web_login")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: UserRegistrationForm) -> HttpResponse:
        response = super().form_valid(form)
        EmailVerificationToken.objects.create(user=self.object)
        messages.success(self.request, "Cadastro realizado com sucesso! Verifique seu e-mail para confirmar o acesso.")
        return response

    def form_invalid(self, form: UserRegistrationForm) -> HttpResponse:
        messages.error(self.request, "Erro no cadastro. Verifique os dados e tente novamente.")
        return super().form_invalid(form)


@method_decorator([csrf_protect, never_cache], name="dispatch")
class LoginView(FormView):
    form_class = UserLoginForm
    template_name = "accounts/login.html"
    success_url = reverse_lazy("home")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: UserLoginForm) -> HttpResponse:
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=username, password=password)
        if user is None:
            messages.error(self.request, "Credenciais inválidas.")
            try:
                suspected_user = User.objects.get(username=username)
            except User.DoesNotExist:
                suspected_user = None
            if suspected_user:
                _record_security_event(self.request, suspected_user, "login_failed")
            return super().form_invalid(form)

        login(self.request, user)
        if form.cleaned_data.get("remember_me"):
            self.request.session.set_expiry(1209600)
        else:
            self.request.session.set_expiry(0)

        messages.success(self.request, f"Bem-vindo(a), {user.first_name or user.username}!")
        _record_security_event(self.request, user, "login_success")

        next_url = self.request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("dashboards:main")

    def form_invalid(self, form: UserLoginForm) -> HttpResponse:
        messages.error(self.request, "Credenciais inválidas. Verifique seus dados e tente novamente.")
        return super().form_invalid(form)


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    user_name = request.user.first_name or request.user.username
    _record_security_event(request, request.user, "logout")
    logout(request)
    messages.success(request, f"Até logo, {user_name}!")
    return redirect("accounts:web_login")


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            _record_security_event(request, request.user, "profile_update")
            return redirect("accounts:profile")
        messages.error(request, "Erro ao atualizar perfil. Verifique os dados.")
    else:
        form = UserProfileForm(instance=request.user)

    context = {"form": form, "user": request.user}
    return render(request, "accounts/profile.html", context)


@login_required
def profile_detail_view(request: HttpRequest, pk: int | None = None) -> HttpResponse:
    profile_user = get_object_or_404(User, pk=pk) if pk else request.user
    if not (request.user == profile_user or request.user.is_staff or request.user.is_leader()):
        raise Http404("Você não tem permissão para visualizar este perfil.")

    user_skills = profile_user.user_skills.select_related("skill__category").order_by("-level")
    team_memberships = TeamMembership.objects.filter(user=profile_user, is_active=True).select_related("team")
    active_projects = (
        Project.objects.filter(Q(team__memberships__user=profile_user) | Q(created_by=profile_user))
        .select_related("team")
        .distinct()
    )

    context = {
        "profile_user": profile_user,
        "user_skills": user_skills,
        "team_memberships": team_memberships,
        "active_projects": active_projects,
    }
    return render(request, "accounts/profile_detail.html", context)


@login_required
def collaborator_search_page(request: HttpRequest) -> HttpResponse:
    available_skills = Skill.objects.filter(is_active=True).order_by("name")
    selected_skills = request.GET.getlist("skill")
    min_level = int(request.GET.get("min_level", 3))

    results = []
    if selected_skills:
        user_skills_qs = (
            UserSkill.objects.filter(level__gte=min_level, skill__name__in=selected_skills)
            .select_related("skill", "user")
        )
        collaborator_ids = user_skills_qs.values_list("user_id", flat=True).distinct()
        collaborators = User.objects.filter(id__in=collaborator_ids)
        for collaborator in collaborators:
            collaborator_skills = [
                {
                    "name": user_skill.skill.name,
                    "level": user_skill.level,
                }
                for user_skill in user_skills_qs.filter(user=collaborator)
            ]
            results.append({"user": collaborator, "skills": collaborator_skills})

    context = {
        "available_skills": available_skills,
        "selected_skills": selected_skills,
        "min_level": min_level,
        "results": results,
    }
    return render(request, "accounts/collaborator_search.html", context)


@login_required
def bulk_import_view(request: HttpRequest) -> HttpResponse:
    if not (request.user.is_staff or request.user.is_leader()):
        raise Http404("Página não encontrada")

    form = CollaboratorImportForm(request.POST or None, request.FILES or None)
    import_summary: list[dict[str, str]] = []

    if request.method == "POST" and form.is_valid():
        default_role = form.cleaned_data["default_role"]
        send_welcome = form.cleaned_data["send_welcome_email"]

        try:
            with transaction.atomic():
                for row in form.iter_rows():
                    username = (row.get("username") or row.get("login") or "").strip()
                    email = (row.get("email") or "").strip()
                    if not username or not email:
                        import_summary.append({"username": username or "<sem usuário>", "status": "Dados incompletos"})
                        continue

                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            "email": email,
                            "first_name": row.get("first_name") or row.get("nome") or "",
                            "last_name": row.get("last_name") or row.get("sobrenome") or "",
                        },
                    )

                    if created:
                        password = row.get("password") or User.objects.make_random_password()
                        user.set_password(password)
                        user.role = row.get("role") or default_role
                        user.save()
                        token = EmailVerificationToken.objects.create(user=user)
                        import_summary.append({"username": username, "status": "Importado", "token": token.token})
                        if send_welcome:
                            logger.info("Simulação de envio de boas-vindas para %s", email)
                    else:
                        import_summary.append({"username": username, "status": "Já existente"})

            messages.success(request, "Importação concluída. Confira o resumo abaixo.")
        except ValidationError as exc:
            form.add_error("file", exc.message)
        except Exception as exc:  # pragma: no cover - falha inesperada
            form.add_error(None, f"Erro ao processar arquivo: {exc}")

    return render(
        request,
        "accounts/import.html",
        {"form": form, "import_summary": import_summary},
    )


@login_required
def user_management_view(request: HttpRequest) -> HttpResponse:
    if not (request.user.is_staff or request.user.is_leader()):
        raise Http404("Página não encontrada")

    users = User.objects.all().order_by("date_joined")
    forms_by_user = {user.pk: UserRoleForm(prefix=str(user.pk), instance=user) for user in users}

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        target_user = get_object_or_404(User, pk=user_id)
        form = UserRoleForm(request.POST, prefix=str(target_user.pk), instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Permissões de {target_user.username} atualizadas com sucesso!")
            return redirect("accounts:user_management")
        forms_by_user[target_user.pk] = form

    context = {
        "users": users,
        "forms_by_user": forms_by_user,
    }
    return render(request, "accounts/user_management.html", context)


def home_view(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("accounts:web_login")
    return redirect("dashboards:main")


@login_required
def special_admin_view(request: HttpRequest) -> HttpResponse:
    from .profile_views import admin_dashboard

    if not request.user.is_superuser:
        raise Http404("Página não encontrada")

    special_token = request.session.get("special_admin_token") or request.GET.get("token")
    if special_token == "admin_access_xmen_2024":
        request.session["special_admin_token"] = "admin_access_xmen_2024"
        return admin_dashboard(request)

    raise Http404("Página não encontrada")
