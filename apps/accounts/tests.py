from __future__ import annotations

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import EmailVerificationToken, User


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_registration_creates_verification_token(self):
        payload = {
            "username": "jane",
            "email": "jane@example.com",
            "password": "SuperSecure123",
            "password_confirm": "SuperSecure123",
            "first_name": "Jane",
            "last_name": "Doe",
            "role": "collaborator",
            "bio": "",
            "position": "Designer",
            "department": "Produto",
            "availability_hours": 6,
        }

        response = self.client.post(reverse("accounts:api_register"), payload, format="json")
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username="jane")
        token = EmailVerificationToken.objects.get(user=user)
        self.assertIn("verification_token", response.data)
        self.assertEqual(response.data["verification_token"], token.token)
        self.assertFalse(user.is_email_verified)

    def test_login_requires_email_verification(self):
        user = User.objects.create_user(
            username="mike",
            email="mike@example.com",
            password="TestPassword123",
            first_name="Mike",
            last_name="Smith",
        )
        EmailVerificationToken.objects.create(user=user)

        response = self.client.post(
            reverse("accounts:api_login"),
            {"username": "mike", "password": "TestPassword123"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("É necessário confirmar o e-mail", str(response.data))

        token = user.verification_tokens.latest("created_at")
        verify_response = self.client.post(reverse("accounts:api_verify_email"), {"token": token.token}, format="json")
        self.assertEqual(verify_response.status_code, 200)

        login_response = self.client.post(
            reverse("accounts:api_login"),
            {"username": "mike", "password": "TestPassword123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("tokens", login_response.data)

    def test_oauth_login_simulation(self):
        user = User.objects.create_user(
            username="oauth-user",
            email="oauth@example.com",
            password="StrongPassword321",
            first_name="OAuth",
            last_name="User",
        )
        EmailVerificationToken.objects.create(user=user).mark_confirmed()

        response = self.client.post(
            reverse("accounts:api_oauth_login"),
            {
                "provider": "google",
                "access_token": "elgoog-12345",
                "email": "oauth@example.com",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("tokens", response.data)


class CollaboratorSearchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="leader",
            email="leader@example.com",
            password="LeaderPass123",
            role="leader",
        )
        EmailVerificationToken.objects.create(user=self.user).mark_confirmed()
        self.client.force_authenticate(self.user)

        self.collaborator = User.objects.create_user(
            username="colab",
            email="colab@example.com",
            password="CollabPass123",
            role="collaborator",
        )
        EmailVerificationToken.objects.create(user=self.collaborator).mark_confirmed()

        from apps.skills.models import Skill, SkillCategory, UserSkill

        category = SkillCategory.objects.create(name="Tecnologia")
        self.skill = Skill.objects.create(name="Python", category=category)
        UserSkill.objects.create(user=self.collaborator, skill=self.skill, level=4)

    def test_search_by_skill(self):
        response = self.client.get(reverse("accounts:api_collaborator_search"), {"skill": [self.skill.name]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["full_name"], self.collaborator.full_name)


class HRIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="hr_leader",
            email="hr@example.com",
            password="TestPass123",
            role="leader",
        )
        EmailVerificationToken.objects.create(user=self.user).mark_confirmed()
        self.client.force_authenticate(self.user)

    def test_hr_sync_returns_user_payload(self):
        response = self.client.get(reverse("accounts:api_hr_sync"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
