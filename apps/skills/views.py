"""Views for skill management and UI."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from .forms import CompetencySelectionForm
from .models import Skill, SkillCategory, UserSkill
from .serializers import SkillCategorySerializer, SkillSerializer, UserSkillSerializer


@extend_schema_view(
    list=extend_schema(tags=["Skills"], summary="Listar categorias de habilidades"),
    create=extend_schema(tags=["Skills"], summary="Criar categoria"),
    retrieve=extend_schema(tags=["Skills"], summary="Detalhes da categoria"),
    update=extend_schema(tags=["Skills"], summary="Atualizar categoria"),
    destroy=extend_schema(tags=["Skills"], summary="Excluir categoria"),
)
class SkillCategoryViewSet(viewsets.ModelViewSet):
    queryset = SkillCategory.objects.all()
    serializer_class = SkillCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["Skills"], summary="Listar habilidades"),
    create=extend_schema(tags=["Skills"], summary="Criar habilidade"),
    retrieve=extend_schema(tags=["Skills"], summary="Detalhes da habilidade"),
    update=extend_schema(tags=["Skills"], summary="Atualizar habilidade"),
    destroy=extend_schema(tags=["Skills"], summary="Excluir habilidade"),
)
class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.filter(is_active=True)
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset


@extend_schema_view(
    list=extend_schema(tags=["User Skills"], summary="Listar habilidades do usuário"),
    create=extend_schema(tags=["User Skills"], summary="Adicionar habilidade"),
    retrieve=extend_schema(tags=["User Skills"], summary="Detalhes da habilidade"),
    update=extend_schema(tags=["User Skills"], summary="Atualizar nível"),
    destroy=extend_schema(tags=["User Skills"], summary="Remover habilidade"),
)
class UserSkillViewSet(viewsets.ModelViewSet):
    queryset = UserSkill.objects.all()
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_leader() or self.request.user.is_staff:
            return UserSkill.objects.all()
        return UserSkill.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if not serializer.validated_data.get("user"):
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @extend_schema(
        tags=["User Skills"],
        summary="Validar habilidade",
        description="Validar habilidade de um usuário (apenas líderes)",
    )
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def validate_skill(self, request, pk=None):
        if not request.user.is_leader() and not request.user.is_staff:
            return Response({"error": "Apenas líderes podem validar habilidades"}, status=status.HTTP_403_FORBIDDEN)

        user_skill = self.get_object()
        user_skill.is_validated = True
        user_skill.validated_by = request.user
        user_skill.validated_at = timezone.now()
        user_skill.save()

        return Response({"message": "Habilidade validada com sucesso"})

    @extend_schema(
        tags=["User Skills"],
        summary="Habilidades por usuário",
        description="Buscar habilidades de um usuário específico",
    )
    @action(detail=False, methods=["get"])
    def by_user(self, request):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"error": "Parâmetro user_id é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        user_skills = UserSkill.objects.filter(user_id=user_id)
        serializer = self.get_serializer(user_skills, many=True)
        return Response(serializer.data)


@login_required
def skill_list(request):
    all_user_skills = UserSkill.objects.select_related("skill", "user")
    user_skills = all_user_skills.filter(user=request.user)

    total_skills = Skill.objects.filter(is_active=True).count()
    my_skills = user_skills.count()
    team_skills = all_user_skills.values("skill").distinct().count()
    skill_categories = SkillCategory.objects.count()

    skills = Skill.objects.filter(is_active=True).select_related("category")
    for skill in skills:
        user_skill = user_skills.filter(skill=skill).first()
        skill.proficiency = user_skill.level * 25 if user_skill else 0
        skill.user = request.user if user_skill else None
        skill.endorsement_count = 0

    context = {
        "skills": skills,
        "total_skills": total_skills,
        "my_skills": my_skills,
        "team_skills": team_skills,
        "skill_categories": skill_categories,
        "user_skills": user_skills,
    }
    return render(request, "skills/list.html", context)


@login_required
def skill_detail(request, pk):
    skill = get_object_or_404(Skill, pk=pk, is_active=True)
    user_skill = UserSkill.objects.filter(user=request.user, skill=skill).first()

    context = {
        "skill": skill,
        "user_skill": user_skill,
    }
    return render(request, "skills/detail.html", context)


@login_required
def add_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id, is_active=True)
    user_skill, created = UserSkill.objects.get_or_create(user=request.user, skill=skill, defaults={"level": 1})

    if created:
        messages.success(request, f'Habilidade "{skill.name}" adicionada ao seu perfil!')
    else:
        messages.info(request, f'Você já possui a habilidade "{skill.name}".')

    return render(request, "skills/detail.html", {"skill": skill, "user_skill": user_skill})


@login_required
def skill_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category")
        description = request.POST.get("description")

        if not name or not category_id:
            messages.error(request, "Informe nome e categoria.")
        else:
            category = get_object_or_404(SkillCategory, pk=category_id)
            Skill.objects.create(name=name, category=category, description=description)
            messages.success(request, "Habilidade criada com sucesso!")
            return redirect("skills:list")

    context = {
        "categories": SkillCategory.objects.all(),
    }
    return render(request, "skills/create.html", context)


@login_required
def edit_competencies(request):
    form = CompetencySelectionForm(user=request.user, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Competências atualizadas com sucesso!")
        return redirect("skills:edit")

    user_skills = (
        UserSkill.objects.filter(user=request.user)
        .select_related("skill__category")
        .order_by("-level")
    )

    context = {
        "form": form,
        "user_skills": user_skills,
        "has_skills": user_skills.exists(),
    }
    return render(request, "skills/edit.html", context)


@login_required
def add_user_skill(request):
    if request.method == "POST":
        skill_id = request.POST.get("skill")
        level = int(request.POST.get("level", 1))
        skill = get_object_or_404(Skill, pk=skill_id)
        UserSkill.objects.update_or_create(user=request.user, skill=skill, defaults={"level": level})
        messages.success(request, "Habilidade atribuída ao colaborador.")
    return redirect("skills:list")


@login_required
def remove_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    UserSkill.objects.filter(user=request.user, skill=skill).delete()
    messages.success(request, "Habilidade removida do perfil.")
    return redirect("skills:list")


@login_required
def update_skill_level(request, skill_id):
    if request.method == "POST":
        new_level = int(request.POST.get("level", 1))
        user_skill = get_object_or_404(UserSkill, user=request.user, skill_id=skill_id)
        user_skill.level = new_level
        user_skill.save()
        messages.success(request, "Nível da habilidade atualizado.")
    return redirect("skills:detail", pk=skill_id)
