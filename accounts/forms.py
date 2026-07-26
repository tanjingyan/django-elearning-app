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