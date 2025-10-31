from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MembershipPlan

User = get_user_model()


class MembershipViewsTests(TestCase):
    def setUp(self):
        self.plan = MembershipPlan.objects.create(
            name="Monthly", slug="monthly", price=49.99, duration_days=30
        )
        self.user = User.objects.create_user("testuser", "test@example.com", "pass12345")

    def test_plan_list(self):
        response = self.client.get(reverse("memberships:plan_list"))
        self.assertEqual(response.status_code, 200)

    def test_subscribe_requires_login(self):
        response = self.client.get(reverse("memberships:subscribe", args=[self.plan.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_subscribe_flow(self):
        self.client.login(username="testuser", password="pass12345")
        response = self.client.post(
            reverse("memberships:subscribe", args=[self.plan.slug]),
            {"auto_renew": True},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.membership_set.filter(plan=self.plan).exists())
