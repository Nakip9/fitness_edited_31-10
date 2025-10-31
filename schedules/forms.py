from django import forms

from .models import ClassBooking


class ClassBookingForm(forms.ModelForm):
    class Meta:
        model = ClassBooking
        fields = ()
