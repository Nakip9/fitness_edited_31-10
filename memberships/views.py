from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from payments.models import PaymentRequest

from .forms import MembershipContactForm
from .models import Membership, MembershipPlan


class MembershipPlanListView(ListView):
    template_name = "memberships/plan_list.html"
    queryset = MembershipPlan.objects.filter(is_active=True)
    context_object_name = "plans"


class MembershipPlanDetailView(DetailView):
    template_name = "memberships/plan_detail.html"
    model = MembershipPlan
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "plan"


@login_required
def subscribe(request, slug):
    plan = get_object_or_404(MembershipPlan, slug=slug, is_active=True)
    plans = MembershipPlan.objects.filter(is_active=True)
    if request.method == "POST":
        form = MembershipContactForm(request.POST, plans=plans)
        if form.is_valid():
            selected_plan = form.cleaned_data["plan"]
            phone_number = form.cleaned_data["phone_number"]
            membership = (
                Membership.objects.filter(
                    user=request.user,
                    plan=selected_plan,
                    status="pending",
                )
                .order_by("-start_date")
                .first()
            )
            if membership is None:
                membership = Membership.objects.create(
                    user=request.user,
                    plan=selected_plan,
                    start_date=timezone.now(),
                    status="pending",
                )
            PaymentRequest.objects.create(
                user=request.user,
                plan=selected_plan,
                phone_number=phone_number,
                notes=f"Membership #{membership.pk} pending activation",
            )
            messages.success(
                request,
                "Thank you! Our customer service team will contact you within 2 hours to finalize your membership.",
            )
            return redirect("memberships:plan_detail", slug=selected_plan.slug)
    else:
        form = MembershipContactForm(plans=plans, initial_plan=plan)

    selected_plan_value = form["plan"].value() or (str(plans.first().pk) if plans else "")
    return render(
        request,
        "memberships/subscribe.html",
        {
            "plan": plan,
            "plans": plans,
            "form": form,
            "selected_plan": selected_plan_value,
        },
    )


@login_required
def my_memberships(request):
    memberships = Membership.objects.filter(user=request.user)
    return render(request, "memberships/my_memberships.html", {"memberships": memberships})
