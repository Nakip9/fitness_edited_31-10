from django.urls import path

from . import views

app_name = "schedules"

urlpatterns = [
    path("", views.ScheduleListView.as_view(), name="schedule"),
    path("<slug:slug>/", views.GymClassDetailView.as_view(), name="class_detail"),
    path("<slug:slug>/book/", views.book_class, name="book_class"),
]
