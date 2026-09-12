from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser, StatusUpdate


# =========================================================
# USER REGISTRATION FORM
# =========================================================

class CustomUserCreationForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
            }
        ),
    )

    first_name = forms.CharField(
        required=True,
        max_length=150,
    )

    last_name = forms.CharField(
        required=True,
        max_length=150,
    )


    class Meta:

        model = CustomUser

        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )


    def clean_email(self):

        email = (
            self.cleaned_data
            .get(
                "email",
                "",
            )
            .strip()
            .lower()
        )

        if not email:

            raise forms.ValidationError(
                "Please enter an email address."
            )

        if (
            CustomUser.objects
            .filter(
                email__iexact=email
            )
            .exists()
        ):

            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email


    def save(
        self,
        commit=True,
    ):

        user = super().save(
            commit=False
        )

        user.email = (
            self.cleaned_data["email"]
        )

        user.first_name = (
            self.cleaned_data["first_name"]
        )

        user.last_name = (
            self.cleaned_data["last_name"]
        )

        user.role = "student"

        if commit:

            user.save()

        return user



# =========================================================
# STATUS UPDATE FORM
# =========================================================

class StatusUpdateForm(forms.ModelForm):

    class Meta:

        model = StatusUpdate

        fields = [
            "content",
        ]

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Share an update...",
                }
            ),
        }



# =========================================================
# EDIT PROFILE FORM
# =========================================================

class EditProfileForm(forms.ModelForm):

    class Meta:

        model = CustomUser

        fields = [
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "bio",
        ]

        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),
        }


    def clean_email(self):

        email = (
            self.cleaned_data
            .get(
                "email",
                "",
            )
            .strip()
            .lower()
        )

        if not email:

            raise forms.ValidationError(
                "Please enter an email address."
            )

        duplicate_email = (
            CustomUser.objects
            .filter(
                email__iexact=email
            )
            .exclude(
                pk=self.instance.pk
            )
            .exists()
        )

        if duplicate_email:

            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email