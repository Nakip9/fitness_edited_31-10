from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["price"]

    def __str__(self) -> str:
        return self.name

    @property
    def duration(self) -> timedelta:
        return timedelta(days=self.duration_days)


class MembershipBenefit(models.Model):
    plan = models.ForeignKey(
        MembershipPlan, related_name="benefits", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    highlight = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.text} ({self.plan})"


class Membership(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("expired", "Expired"),
        ("canceled", "Canceled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    auto_renew = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_date"]
        unique_together = ("user", "plan", "start_date")

    def __str__(self) -> str:
        return f"{self.user} - {self.plan}"

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + self.plan.duration
        super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        if self.status != "active":
            return False
        return self.end_date >= timezone.now()
