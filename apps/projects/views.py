"""Views related to project management."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.skills.models import SkillRequirement
from apps.tasks.models import Task

from .forms import ProjectForm, ReportFilterForm, SkillRequirementFormSet
from .models import KeyResult, OKR, Project, Sprint
from .serializers import KeyResultSerializer, OKRSerializer, ProjectSerializer, SprintSerializer


@extend_schema_view(
    list=extend_schema(tags=["Projects"], summary="Listar projetos"),
    create=extend_schema(tags=["Projects"], summary="Criar projeto"),
    retrieve=extend_schema(tags=["Projects"], summary="Detalhes do projeto"),
    update=extend_schema(tags=["Projects"], summary="Atualizar projeto"),
    destroy=extend_schema(tags=["Projects"], summary="Excluir projeto"),
)
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.exclude(status__in=["cancelled", "completed"])
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Project.objects.all()
        return (
            Project.objects.filter(
                models.Q(team__memberships__user=self.request.user) | models.Q(created_by=self.request.user)
            )
            .exclude(status__in=["cancelled", "completed"])
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def sprints(self, request, pk=None):
        project = self.get_object()
        serializer = SprintSerializer(project.sprints.all().order_by("-start_date"), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def okrs(self, request, pk=None):
        project = self.get_object()
        serializer = OKRSerializer(project.okrs.all().order_by("-created_at"), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        project = self.get_object()
        project.status = "completed"
        project.save()
        return Response({"message": "Projeto arquivado com sucesso"})


@extend_schema_view(
    list=extend_schema(tags=["Sprints"], summary="Listar sprints"),
    create=extend_schema(tags=["Sprints"], summary="Criar sprint"),
    retrieve=extend_schema(tags=["Sprints"], summary="Detalhes do sprint"),
    update=extend_schema(tags=["Sprints"], summary="Atualizar sprint"),
    destroy=extend_schema(tags=["Sprints"], summary="Excluir sprint"),
)
class SprintViewSet(viewsets.ModelViewSet):
    queryset = Sprint.objects.all()
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.request.query_params.get("project")
        if project_id:
            return self.queryset.filter(project_id=project_id)
        return self.queryset.filter(project__team__memberships__user=self.request.user).distinct()

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        sprint = self.get_object()
        sprint.status = "active"
        sprint.start_date = timezone.now().date()
        sprint.save()
        return Response({"message": "Sprint iniciado com sucesso"})

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        sprint = self.get_object()
        sprint.status = "completed"
        sprint.end_date = timezone.now().date()
        sprint.save()
        return Response({"message": "Sprint finalizado com sucesso"})


@extend_schema_view(
    list=extend_schema(tags=["OKRs"], summary="Listar OKRs"),
    create=extend_schema(tags=["OKRs"], summary="Criar OKR"),
    retrieve=extend_schema(tags=["OKRs"], summary="Detalhes do OKR"),
    update=extend_schema(tags=["OKRs"], summary="Atualizar OKR"),
    destroy=extend_schema(tags=["OKRs"], summary="Excluir OKR"),
)
class OKRViewSet(viewsets.ModelViewSet):
    queryset = OKR.objects.all()
    serializer_class = OKRSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.request.query_params.get("project")
        if project_id:
            return self.queryset.filter(project_id=project_id)
        return self.queryset.filter(project__team__memberships__user=self.request.user).distinct()

    @action(detail=True, methods=["get"])
    def key_results(self, request, pk=None):
        okr = self.get_object()
        serializer = KeyResultSerializer(okr.key_results.all(), many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=["Key Results"], summary="Listar Key Results"),
    create=extend_schema(tags=["Key Results"], summary="Criar Key Result"),
    retrieve=extend_schema(tags=["Key Results"], summary="Detalhes do Key Result"),
    update=extend_schema(tags=["Key Results"], summary="Atualizar Key Result"),
    destroy=extend_schema(tags=["Key Results"], summary="Excluir Key Result"),
)
class KeyResultViewSet(viewsets.ModelViewSet):
    queryset = KeyResult.objects.all()
    serializer_class = KeyResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        okr_id = self.request.query_params.get("okr")
        if okr_id:
            return self.queryset.filter(okr_id=okr_id)
        return self.queryset.filter(okr__project__team__memberships__user=self.request.user).distinct()

    @action(detail=True, methods=["post"])
    def update_progress(self, request, pk=None):
        key_result = self.get_object()
        progress = request.data.get("progress", 0)

        try:
            progress = float(progress)
        except (TypeError, ValueError):
            return Response({"error": "Progresso deve ser numérico"}, status=status.HTTP_400_BAD_REQUEST)

        if 0 <= progress <= 100:
            key_result.current_value = (key_result.target_value * progress) / 100
            key_result.save()
            return Response({"message": "Progresso atualizado com sucesso"})

        return Response({"error": "Progresso deve estar entre 0 e 100"}, status=status.HTTP_400_BAD_REQUEST)


@login_required
def project_list(request):
    projects = Project.objects.all().order_by("-created_at")

    total_projects = projects.count()
    active_projects = projects.filter(status="active").count()
    completed_projects = projects.filter(status="completed").count()
    delayed_projects = (
        projects.filter(status="active", end_date__lt=timezone.now().date()).count() if total_projects > 0 else 0
    )

    for project in projects:
        project.team_members = project.team.memberships.count() if project.team else 0
        project.overdue = project.status == "active" and project.end_date < timezone.now().date()

    context = {
        "projects": projects,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "delayed_projects": delayed_projects,
    }
    return render(request, "projects/list.html", context)


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = Task.objects.filter(project=project)
    sprints = project.sprints.all().order_by("-start_date")
    okrs = project.okrs.all().order_by("-created_at")

    context = {
        "project": project,
        "tasks": tasks,
        "sprints": sprints,
        "okrs": okrs,
    }
    return render(request, "projects/detail.html", context)


@login_required
def project_create(request):
    requirement_formset = SkillRequirementFormSet(prefix="requirements")
    if request.method == "POST":
        form = ProjectForm(request.POST)
        requirement_formset = SkillRequirementFormSet(request.POST, prefix="requirements")
        if form.is_valid() and requirement_formset.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()

            for requirement_form in requirement_formset:
                if requirement_form.cleaned_data.get("DELETE"):
                    continue
                skill = requirement_form.cleaned_data.get("skill")
                if not skill:
                    continue
                SkillRequirement.objects.create(
                    content_object=project,
                    skill=skill,
                    min_level=int(requirement_form.cleaned_data.get("min_level", 1)),
                    is_mandatory=requirement_form.cleaned_data.get("is_mandatory", False),
                )

            messages.success(request, "Projeto criado com sucesso!")
            return redirect("projects:detail", pk=project.pk)
        messages.error(request, "Corrija os erros antes de continuar.")
    else:
        form = ProjectForm()

    return render(
        request,
        "projects/create.html",
        {"form": form, "requirement_formset": requirement_formset},
    )


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    content_type = ContentType.objects.get_for_model(Project)
    existing_requirements = SkillRequirement.objects.filter(
        content_type=content_type, object_id=project.pk
    )
    initial_requirements = [
        {
            "skill": requirement.skill_id,
            "min_level": requirement.min_level,
            "is_mandatory": requirement.is_mandatory,
        }
        for requirement in existing_requirements
    ]

    requirement_formset = SkillRequirementFormSet(
        prefix="requirements", initial=initial_requirements or None
    )

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        requirement_formset = SkillRequirementFormSet(request.POST, prefix="requirements")
        if form.is_valid() and requirement_formset.is_valid():
            form.save()
            existing_requirements.delete()
            for requirement_form in requirement_formset:
                if requirement_form.cleaned_data.get("DELETE"):
                    continue
                skill = requirement_form.cleaned_data.get("skill")
                if not skill:
                    continue
                SkillRequirement.objects.create(
                    content_object=project,
                    skill=skill,
                    min_level=int(requirement_form.cleaned_data.get("min_level", 1)),
                    is_mandatory=requirement_form.cleaned_data.get("is_mandatory", False),
                )
            messages.success(request, "Projeto atualizado com sucesso!")
            return redirect("projects:detail", pk=project.pk)
        messages.error(request, "Corrija os erros antes de continuar.")
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/create.html",
        {"form": form, "project": project, "requirement_formset": requirement_formset},
    )


@login_required
def active_projects_view(request):
    projects = (
        Project.objects.filter(status="active")
        .select_related("team", "created_by")
        .prefetch_related("team__memberships__user")
        .order_by("end_date")
    )

    project_details = []
    for project in projects:
        members = []
        if project.team:
            members = [
                membership.user
                for membership in project.team.memberships.filter(is_active=True).select_related("user")
            ]
        project_details.append(
            {
                "project": project,
                "members": members,
                "progress": project.progress_percentage,
                "is_overdue": project.is_overdue,
            }
        )

    return render(request, "projects/active.html", {"project_details": project_details})


@login_required
def report_generator(request):
    form = ReportFilterForm(user=request.user, data=request.POST or None)
    preview = None

    if request.method == "POST" and form.is_valid():
        projects_qs = Project.objects.all()
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        include_completed = form.cleaned_data.get("include_completed")
        team = form.cleaned_data.get("team")

        if start_date:
            projects_qs = projects_qs.filter(start_date__gte=start_date)
        if end_date:
            projects_qs = projects_qs.filter(end_date__lte=end_date)
        if not include_completed:
            projects_qs = projects_qs.exclude(status="completed")
        if team:
            projects_qs = projects_qs.filter(team=team)

        projects_qs = projects_qs.select_related("team", "created_by")
        preview = {
            "total_projects": projects_qs.count(),
            "total_hours": projects_qs.aggregate(total=models.Sum("estimated_hours"))["total"] or 0,
            "projects": projects_qs[:10],
        }

    return render(
        request,
        "projects/report_generator.html",
        {"form": form, "preview": preview},
    )
