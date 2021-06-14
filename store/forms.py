from django import forms
from django.forms.widgets import CheckboxInput, TextInput
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "1234 Main St"
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Apartment or suite"
    }))
    country = CountryField(blank_label="(select country)").formfield(
        widget=CountrySelectWidget(
            attrs={"class": "custom-select d-block w-100"})
    )
    zip_code = forms.CharField(widget=TextInput(attrs={
        "class": "form-control"
    }))
    same_billing_address = forms.BooleanField(widget=forms.CheckboxInput(attrs={
        "class": "custom-control-input"
    }), required=False)
    save_info = forms.BooleanField(widget=CheckboxInput(attrs={
        "class": "custom-control-input"
    }), required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={
            "class": "custom-control custom-radio"
        }), choices=PAYMENT_CHOICES)
