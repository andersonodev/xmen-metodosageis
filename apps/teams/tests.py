from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import EmailVerificationToken, User
from apps.projects.models import Project
from apps.skills.models import Skill, SkillCategory, UserSkill

from .forms import TeamCompositionDraftForm
from .models import TeamCompositionDraft


class TeamCompositionDraftFormTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="leader",
            email="leader@example.com",
            password="Password123",
            role="leader",
        )
        EmailVerificationToken.objects.create(user=self.owner).mark_confirmed()
        category = SkillCategory.objects.create(name="Tecnologia")
        self.skill = Skill.objects.create(name="Python", category=category)
        project = Project.objects.create(
            name="Projeto Ágil",
            description="Projeto para testes",
            status="planning",
            priority=2,
            start_date="2024-01-01",
            end_date="2024-02-01",
            created_by=self.owner,
        )
        self.project = project
        self.collaborator = User.objects.create_user(
            username="colab",
            email="colab@example.com",
            password="Password123",
        )
        EmailVerificationToken.objects.create(user=self.collaborator).mark_confirmed()
        UserSkill.objects.create(user=self.collaborator, skill=self.skill, level=3)

    def test_form_persists_member_selection(self):
        form = TeamCompositionDraftForm(
            owner=self.owner,
            data={
                "name": "Time Discovery",
                "project": self.project.id,
                "notes": "Preparar squad multidisciplinar",
                "selected_members": [self.collaborator.id],
            },
        )
        self.assertTrue(form.is_valid())
        draft = form.save()
        self.assertEqual(draft.owner, self.owner)
        self.assertEqual(draft.project, self.project)
        self.assertIn(self.collaborator.id, draft.data["members"])


class TeamDraftWebViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="leader",
            email="leader@example.com",
            password="Password123",
            role="leader",
        )
        EmailVerificationToken.objects.create(user=self.owner).mark_confirmed()
        self.client.force_login(self.owner)
        self.project = Project.objects.create(
            name="Projeto Web",
            description="Projeto com rascunho",
            status="planning",
            priority=1,
            start_date="2024-03-01",
            end_date="2024-05-01",
            created_by=self.owner,
        )

    def test_create_draft_via_view(self):
        response = self.client.post(
            reverse("teams:draft_new"),
            {
                "name": "Rascunho Frontend",
                "project": self.project.id,
                "notes": "Priorizar habilidades de UX",
                "selected_members": [],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TeamCompositionDraft.objects.count(), 1)
        draft = TeamCompositionDraft.objects.first()
        self.assertEqual(draft.name, "Rascunho Frontend")
