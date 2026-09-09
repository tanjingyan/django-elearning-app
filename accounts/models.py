from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta
from django.utils import timezone

class CustomUser(AbstractUser):
    STUDENT = "student"
    TEACHER = "teacher"

    ROLE_CHOICES = [
        (STUDENT, "Student"),
        (TEACHER, "Teacher"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=STUDENT,
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )

    bio = models.TextField(
        blank=True,
    )

    def __str__(self):
        return self.username


class StatusUpdate(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def is_older_than_24_hours(self):
        return (
            timezone.now() - self.created_at
            >= timedelta(hours=24)
        )