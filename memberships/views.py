from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from .forms import MembershipSignupForm
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
    membership = Membership.objects.filter(user=request.user, plan=plan).first()
    if request.method == "POST":
        form = MembershipSignupForm(request.POST, instance=membership)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.user = request.user
            membership.plan = plan
            membership.start_date = timezone.now()
            membership.end_date = None
            membership.status = "pending"
            membership.save()
            messages.success(
                request,
                "Membership created. Complete payment to activate the {plan} plan.".format(
                    plan=plan.name
                ),
            )
            return redirect("payments:create", slug=plan.slug)
    else:
        form = MembershipSignupForm(instance=membership)
    return render(
        request,
        "memberships/subscribe.html",
        {
            "plan": plan,
            "form": form,
            "membership": membership,
        },
    )


@login_required
def my_memberships(request):
    memberships = Membership.objects.filter(user=request.user)
    return render(request, "memberships/my_memberships.html", {"memberships": memberships})
