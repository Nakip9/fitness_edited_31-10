from django.urls import path

from . import views

app_name = "memberships"

urlpatterns = [
    path("", views.MembershipPlanListView.as_view(), name="plan_list"),
    path("my/", views.my_memberships, name="my_memberships"),
    path("<slug:slug>/", views.MembershipPlanDetailView.as_view(), name="plan_detail"),
    path("<slug:slug>/subscribe/", views.subscribe, name="subscribe"),
]
