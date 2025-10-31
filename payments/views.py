from __future__ import annotations

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from memberships.models import Membership, MembershipPlan

from .models import Payment

logger = logging.getLogger(__name__)


def _activate_membership(membership: Membership) -> None:
    if membership.status != "active":
        membership.status = "active"
        membership.end_date = timezone.now() + membership.plan.duration
        membership.save(update_fields=["status", "end_date"])


@login_required
def create_checkout(request: HttpRequest, slug: str) -> HttpResponse:
    plan = get_object_or_404(MembershipPlan, slug=slug, is_active=True)
    membership = (
        Membership.objects.filter(user=request.user, plan=plan)
        .order_by("-start_date")
        .first()
    )
    if membership is None:
        messages.error(request, "Please subscribe to the plan before starting payment.")
        return redirect("memberships:plan_detail", slug=slug)

    payment = Payment.objects.create(
        user=request.user,
        plan=plan,
        membership=membership,
        amount=plan.price,
        currency="usd",
    )

    stripe_key = settings.STRIPE_SECRET_KEY
    if stripe_key:
        try:
            import stripe

            stripe.api_key = stripe_key
            session = stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": payment.currency,
                            "product_data": {"name": plan.name},
                            "unit_amount": int(payment.amount * 100),
                        },
                        "quantity": 1,
                    }
                ],
                metadata={"payment_id": payment.pk},
                success_url=request.build_absolute_uri(
                    reverse("payments:success", args=[payment.pk])
                ),
                cancel_url=request.build_absolute_uri(
                    reverse("payments:cancel", args=[payment.pk])
                ),
            )
            payment.stripe_payment_intent = session.get("payment_intent", "")
            payment.save(update_fields=["stripe_payment_intent"])
            return redirect(session.url)
        except Exception as exc:  # pragma: no cover
            logger.exception("Stripe checkout creation failed")
            messages.error(
                request,
                "We were unable to reach the payment provider. Please try again later.",
            )
            payment.status = "failed"
            payment.save(update_fields=["status"])
            return redirect("memberships:plan_detail", slug=slug)

    messages.warning(
        request,
        "Stripe keys are not configured. Membership activated without charging payment.",
    )
    _activate_membership(membership)
    payment.status = "succeeded"
    payment.save(update_fields=["status"])
    return redirect("memberships:my_memberships")


@login_required
def payment_success(request: HttpRequest, pk: int) -> HttpResponse:
    payment = get_object_or_404(Payment, pk=pk, user=request.user)
    _activate_membership(payment.membership)
    payment.status = "succeeded"
    payment.save(update_fields=["status"])
    return render(request, "payments/success.html", {"payment": payment})


@login_required
def payment_cancel(request: HttpRequest, pk: int) -> HttpResponse:
    payment = get_object_or_404(Payment, pk=pk, user=request.user)
    payment.status = "canceled"
    payment.save(update_fields=["status"])
    messages.info(request, "Your payment was cancelled. You can try again anytime.")
    return render(request, "payments/cancel.html", {"payment": payment})
