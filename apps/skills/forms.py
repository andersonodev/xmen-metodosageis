"""Forms dedicated to the collaborator skill management experience."""

from __future__ import annotations

from typing import Iterable

from django import forms
from django.db import transaction

from .models import Skill, SkillCategory, UserSkill


class CompetencySelectionForm(forms.Form):
    """Allow collaborators to curate their technical and behavioural skills."""

    technical_skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.none(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-multiselect",
                "data-placeholder": "Selecione competências técnicas",
            }
        ),
        label="Competências Técnicas",
    )
    behavioral_skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.none(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-multiselect",
                "data-placeholder": "Selecione competências comportamentais",
            }
        ),
        label="Competências Comportamentais",
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        technical_categories, behavioural_categories = self._split_categories()

        self.fields["technical_skills"].queryset = Skill.objects.filter(
            category__in=technical_categories, is_active=True
        ).select_related("category")
        self.fields["behavioral_skills"].queryset = Skill.objects.filter(
            category__in=behavioural_categories, is_active=True
        ).select_related("category")

        current_skills = UserSkill.objects.filter(user=self.user).select_related("skill__category")
        technical_ids, behavioural_ids = [], []
        for user_skill in current_skills:
            if user_skill.skill.category in technical_categories:
                technical_ids.append(user_skill.skill_id)
            else:
                behavioural_ids.append(user_skill.skill_id)

        self.initial.setdefault("technical_skills", technical_ids)
        self.initial.setdefault("behavioral_skills", behavioural_ids)

    def _split_categories(self) -> tuple[Iterable[SkillCategory], Iterable[SkillCategory]]:
        """Split categories in technical and behavioural buckets using heuristics."""

        behavioural_keywords = {"soft", "comportamental", "comportamento"}
        behavioural: list[SkillCategory] = []
        technical: list[SkillCategory] = []

        for category in SkillCategory.objects.all():
            name_normalised = category.name.lower()
            if any(keyword in name_normalised for keyword in behavioural_keywords):
                behavioural.append(category)
            else:
                technical.append(category)

        # Fallback: if one of the buckets is empty we provide a balanced split
        if not technical and behavioural:
            technical = behavioural
        if not behavioural and technical:
            behavioural = technical

        return technical, behavioural

    @transaction.atomic
    def save(self) -> None:
        """Persist the competency selection for the bound user."""

        if not self.is_valid():  # pragma: no cover - guard for misuse
            raise ValueError("Formulário inválido não pode ser salvo")

        selected_skill_ids = set()
        for field_name in ("technical_skills", "behavioral_skills"):
            selected_skill_ids.update(skill.id for skill in self.cleaned_data.get(field_name, []))

        user_skill_qs = UserSkill.objects.filter(user=self.user)
        existing_skill_ids = set(user_skill_qs.values_list("skill_id", flat=True))

        # Remove deselected skills
        deselected_ids = existing_skill_ids - selected_skill_ids
        if deselected_ids:
            user_skill_qs.filter(skill_id__in=deselected_ids).delete()

        # Add or update selected skills
        for skill in Skill.objects.filter(id__in=selected_skill_ids):
            UserSkill.objects.update_or_create(
                user=self.user,
                skill=skill,
                defaults={"level": 3},
            )
