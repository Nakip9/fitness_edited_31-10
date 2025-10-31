from datetime import timedelta

from django.conf import settings
from django.db import models


class ClassCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Class categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class GymClass(models.Model):
    category = models.ForeignKey(ClassCategory, related_name="classes", on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    instructor = models.CharField(max_length=120)
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    capacity = models.PositiveIntegerField(default=20)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self) -> str:
        return self.title

    @property
    def end_time(self):
        return self.start_time + timedelta(minutes=self.duration_minutes)

    @property
    def spots_remaining(self) -> int:
        booked = self.bookings.filter(status="confirmed").count()
        return max(self.capacity - booked, 0)


class ClassBooking(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("waitlist", "Waitlist"),
    ]

    gym_class = models.ForeignKey(GymClass, related_name="bookings", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("gym_class", "user")

    def __str__(self) -> str:
        return f"{self.user} - {self.gym_class} ({self.get_status_display()})"
