from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser, StatusUpdate


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser

        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "profile_picture",
            "bio",
        )

class StatusUpdateForm(forms.ModelForm):

    class Meta:
        model = StatusUpdate

        fields = (
            "content",
        )

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "placeholder": "What's on your mind?",
                    "rows": 4,
                }
            )
        }

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser

        fields = (
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "bio",
        )

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your first name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your last name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your email address",
                }
            ),

            "profile_picture": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),

            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Write a short bio",
                }
            ),
        }