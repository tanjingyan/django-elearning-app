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
            "profile_picture",
            "bio",
        )

    def save(self, commit=True):

        user = super().save(commit=False)

        # All users who register publicly are Students.
        # Teacher accounts must be created/assigned by an administrator.
        user.role = "student"

        if commit:
            user.save()

        return user

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

    def clean_content(self):
        content = self.cleaned_data.get(
            "content",
            "",
        ).strip()

        if not content:
            raise forms.ValidationError(
                "Status update cannot be empty."
            )

        if len(content) > 500:
            raise forms.ValidationError(
                "Status update cannot exceed 500 characters."
            )

        return content


from django import forms

from .models import CustomUser


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


    def clean_email(self):
        email = (
            self.cleaned_data
            .get("email", "")
            .strip()
            .lower()
        )

        # Current user's existing email is allowed.
        if (
            self.instance
            and self.instance.pk
            and self.instance.email
            and self.instance.email.lower() == email
        ):
            return email

        # Another user cannot have the same email.
        if (
            CustomUser.objects
            .filter(email__iexact=email)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError(
                "This email address is already being used."
            )

        return email

    def clean_email(self):
        email = (
            self.cleaned_data
            .get("email", "")
            .strip()
            .lower()
        )

        # Allow the current user to keep their own email.
        if (
            self.instance
            and self.instance.pk
            and self.instance.email
            and self.instance.email.lower() == email
        ):
            return email

        # Reject the email only if ANOTHER user owns it.
        if (
            CustomUser.objects
            .filter(email__iexact=email)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError(
                "This email address is already being used."
            )

        return email
    
    def clean_bio(self):
        bio = self.cleaned_data.get(
            "bio",
            "",
        ).strip()

        if len(bio) > 500:
            raise forms.ValidationError(
                "Bio cannot exceed 500 characters."
            )

        return bio