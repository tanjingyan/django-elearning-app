from django.db import models
from accounts.models import CustomUser
from courses.models import Course


class Notification(models.Model):

    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True
    )

    message = models.CharField(
        max_length=255
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.recipient.username} - "
            f"{self.message}"
        )