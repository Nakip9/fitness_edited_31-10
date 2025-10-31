from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from .forms import ClassBookingForm
from .models import ClassBooking, GymClass


class ScheduleListView(ListView):
    template_name = "schedules/schedule_list.html"
    queryset = GymClass.objects.filter(is_published=True, start_time__gte=timezone.now()).select_related("category")
    context_object_name = "classes"


class GymClassDetailView(DetailView):
    template_name = "schedules/class_detail.html"
    model = GymClass
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "gym_class"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = None
        if self.request.user.is_authenticated:
            booking = ClassBooking.objects.filter(
                gym_class=self.object, user=self.request.user
            ).first()
        context["booking"] = booking
        return context


@login_required
def book_class(request, slug):
    gym_class = get_object_or_404(GymClass, slug=slug, is_published=True)
    booking = ClassBooking.objects.filter(gym_class=gym_class, user=request.user).first()
    if request.method == "POST":
        form = ClassBookingForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.gym_class = gym_class
            booking.user = request.user
            if gym_class.spots_remaining <= 0:
                booking.status = "waitlist"
                messages.info(
                    request,
                    "The class is currently full. You have been added to the waitlist.",
                )
            else:
                booking.status = "confirmed"
                messages.success(request, "Your spot is reserved!")
            booking.save()
            return redirect("schedules:class_detail", slug=gym_class.slug)
    else:
        form = ClassBookingForm(instance=booking)
    return render(
        request,
        "schedules/book_class.html",
        {"gym_class": gym_class, "form": form, "booking": booking},
    )
