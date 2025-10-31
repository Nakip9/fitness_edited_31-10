from django.contrib import admin

from .models import Payment, PaymentRequest


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount", "status", "created_at")
    list_filter = ("status", "plan")
    search_fields = ("user__username", "plan__name", "stripe_payment_intent")


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "plan", "user", "status", "created_at")
    list_filter = ("status", "plan")
    search_fields = ("phone_number", "plan__name", "user__username")
