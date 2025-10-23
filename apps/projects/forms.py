"""Forms for project management."""

from __future__ import annotations

from django import forms

from apps.skills.models import Skill, UserSkill
from apps.teams.models import Team

from .models import Project, Sprint


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "status",
            "priority",
            "start_date",
            "end_date",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome do projeto"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Descrição do projeto"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("A data de término deve ser posterior à data de início.")

        return cleaned_data


class SprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ["name", "goal", "start_date", "end_date"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome do sprint"}),
            "goal": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Objetivo do sprint"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("A data de término deve ser posterior à data de início.")

        return cleaned_data


class SkillRequirementForm(forms.Form):
    skill = forms.ModelChoiceField(
        queryset=Skill.objects.filter(is_active=True).select_related("category"),
        required=False,
        label="Competência",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    min_level = forms.ChoiceField(
        choices=UserSkill.LEVEL_CHOICES,
        initial=3,
        label="Nível mínimo",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    is_mandatory = forms.BooleanField(
        required=False,
        label="Obrigatória",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


SkillRequirementFormSet = forms.formset_factory(
    SkillRequirementForm,
    extra=2,
    can_delete=True,
)


class ReportFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Data inicial",
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Data final",
    )
    team = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Time",
    )
    include_completed = forms.BooleanField(
        required=False,
        initial=False,
        label="Incluir projetos concluídos",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        teams = Team.objects.filter(is_active=True)
        if self.user and not self.user.is_staff:
            teams = teams.filter(memberships__user=self.user).distinct()
        self.fields["team"].queryset = teams.order_by("name")
