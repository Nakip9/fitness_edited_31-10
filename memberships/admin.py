from django.contrib import admin

from .models import Membership, MembershipBenefit, MembershipPlan


class MembershipBenefitInline(admin.TabularInline):
    model = MembershipBenefit
    extra = 1


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration_days", "is_active", "featured")
    list_filter = ("is_active", "featured")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MembershipBenefitInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "start_date", "end_date", "status")
    list_filter = ("status", "plan")
    search_fields = ("user__username", "plan__name")
