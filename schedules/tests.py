from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import ClassCategory, GymClass

User = get_user_model()


class ScheduleTests(TestCase):
    def setUp(self):
        self.category = ClassCategory.objects.create(name="Yoga")
        self.gym_class = GymClass.objects.create(
            category=self.category,
            title="Morning Yoga",
            slug="morning-yoga",
            instructor="Alice",
            start_time=timezone.now() + timedelta(days=1),
            duration_minutes=60,
        )
        self.user = User.objects.create_user("member", "member@example.com", "pass12345")

    def test_schedule_page(self):
        response = self.client.get(reverse("schedules:schedule"))
        self.assertEqual(response.status_code, 200)

    def test_booking_requires_login(self):
        response = self.client.get(reverse("schedules:book_class", args=[self.gym_class.slug]))
        self.assertEqual(response.status_code, 302)

    def test_booking_flow(self):
        self.client.login(username="member", password="pass12345")
        response = self.client.post(reverse("schedules:book_class", args=[self.gym_class.slug]))
        self.assertEqual(response.status_code, 302)
