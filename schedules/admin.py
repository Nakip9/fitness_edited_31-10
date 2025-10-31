from django.contrib import admin

from .models import ClassBooking, ClassCategory, GymClass


@admin.register(ClassCategory)
class ClassCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "start_time", "capacity", "is_published")
    list_filter = ("category", "is_published")
    search_fields = ("title", "instructor")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ClassBooking)
class ClassBookingAdmin(admin.ModelAdmin):
    list_display = ("gym_class", "user", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("gym_class__title", "user__username")
