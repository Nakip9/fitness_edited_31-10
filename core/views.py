from django.shortcuts import render, redirect
from django.http import HttpResponse

from memberships.models import MembershipPlan
from schedules.models import GymClass
from .forms import ContactForm


def home(request):
    plans = MembershipPlan.objects.filter(is_active=True).order_by("price")[:3]
    classes = (
        GymClass.objects.select_related("category")
        .filter(is_published=True)
        .order_by("start_time")[:6]
    )
    return render(request, "core/home.html", {"plans": plans, "classes": classes})


def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save form data to the database
            return redirect('core:contact_thanks')  # Redirect to a thank you page
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {'form': form})

def contact_thanks(request):
    return render(request, 'core/contact_thanks.html')