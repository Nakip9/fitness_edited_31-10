from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from memberships.models import Membership, MembershipPlan

User = get_user_model()


class PaymentViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("payer", "payer@example.com", "pass12345")
        self.plan = MembershipPlan.objects.create(
            name="Annual", slug="annual", price=499.00, duration_days=365
        )
        self.membership = Membership.objects.create(
            user=self.user,
            plan=self.plan,
        )

    def test_create_checkout_without_login_redirects(self):
        response = self.client.get(reverse("payments:create", args=[self.plan.slug]))
        self.assertEqual(response.status_code, 302)

    def test_create_checkout_without_keys(self):
        self.client.login(username="payer", password="pass12345")
        response = self.client.get(reverse("payments:create", args=[self.plan.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("memberships:my_memberships"))
