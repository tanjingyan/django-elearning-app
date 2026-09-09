from django.db import models

from accounts.models import CustomUser
from courses.models import Course


class Notification(models.Model):
    ENROLMENT = "enrolment"
    MATERIAL = "material"

    NOTIFICATION_TYPES = [
        ("enrolment", "Course Enrolment"),
        ("material", "New Material"),
        ("block", "Course Blocked"),
        ("unblock", "Course Unblocked"),
        ("remove", "Removed from Course"),
    ]

    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
    )

    message = models.CharField(
        max_length=255,
    )

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.recipient.username} - "
            f"{self.message}"
        )