from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("<slug:slug>/create/", views.create_checkout, name="create"),
    path("success/<int:pk>/", views.payment_success, name="success"),
    path("cancel/<int:pk>/", views.payment_cancel, name="cancel"),
]
