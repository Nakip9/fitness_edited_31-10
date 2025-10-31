from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount", "status", "created_at")
    list_filter = ("status", "plan")
    search_fields = ("user__username", "plan__name", "stripe_payment_intent")
