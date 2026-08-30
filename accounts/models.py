from django.contrib.auth.models import AbstractUser
from django.db import models


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
        related_name="status_updates",
    )

    content = models.TextField(
        max_length=500,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"