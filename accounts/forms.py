from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email address",
    )

    terms = forms.BooleanField(
        required=True,
        label="I agree to the Terms & Conditions.",
        error_messages={
            "required": "You must agree to the Terms & Conditions to create an account."
        },
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email