from django import forms
from .models import Course, Feedback, CourseMaterial


class CourseForm(forms.ModelForm):

    class Meta:

        model = Course

        fields = (
            "title",
            "description",
            "category",
            "image",
        )

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter course title",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter course description",
                    "rows": 5,
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "image": forms.FileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }

class FeedbackForm(forms.ModelForm):

    class Meta:

        model = Feedback

        fields = (
            "rating",
            "comment",
        )

        widgets = {

            "rating": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 5,
                }
            ),

            "comment": forms.Textarea(
                attrs={
                    "placeholder": "Write your feedback...",
                    "rows": 5,
                }
            ),
        }

class CourseMaterialForm(forms.ModelForm):

    class Meta:

        model = CourseMaterial

        fields = (
            "title",
            "description",
            "file",
        )

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "placeholder": "Enter material title"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "placeholder": "Enter a description of the material",
                    "rows": 5,
                }
            ),

        }