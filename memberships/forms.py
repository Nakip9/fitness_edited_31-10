from django import forms

from .models import Membership


class MembershipSignupForm(forms.ModelForm):
    auto_renew = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Auto renew",
    )

    class Meta:
        model = Membership
        fields = ("auto_renew",)
