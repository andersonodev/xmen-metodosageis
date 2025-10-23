"""Forms for the team management experience."""

from __future__ import annotations

from django import forms
from django.forms import widgets

from apps.accounts.models import User
from apps.projects.models import Project

from .models import TeamCompositionDraft


class TeamCompositionDraftForm(forms.ModelForm):
    """Capture the intent of a team composition before it becomes official."""

    selected_members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-multiselect",
                "data-placeholder": "Selecione colaboradores para o rascunho",
            }
        ),
        label="Colaboradores sugeridos",
        help_text="Escolha os profissionais que farão parte desta composição de equipe.",
    )

    class Meta:
        model = TeamCompositionDraft
        fields = ["name", "project", "notes"]
        widgets = {
            "name": widgets.TextInput(
                attrs={"class": "form-input", "placeholder": "Ex: Squad Discovery"}
            ),
            "project": widgets.Select(attrs={"class": "form-select"}),
            "notes": widgets.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 4,
                    "placeholder": "Detalhes da composição, expectativas e próximos passos.",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("owner")
        super().__init__(*args, **kwargs)

        self.fields["selected_members"].queryset = User.objects.filter(is_active=True).order_by(
            "first_name", "last_name"
        )
        self.fields["project"].queryset = Project.objects.order_by("name")

        if self.instance.pk:
            selected_ids = self.instance.data.get("members", []) if isinstance(self.instance.data, dict) else []
            self.initial.setdefault("selected_members", selected_ids)

    def save(self, commit: bool = True) -> TeamCompositionDraft:
        draft = super().save(commit=False)
        draft.owner = self.owner
        selected_members = list(self.cleaned_data.get("selected_members", []))
        draft.data = {"members": [member.id for member in selected_members]}
        if commit:
            draft.save()
        return draft
