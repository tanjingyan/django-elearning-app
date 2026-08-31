from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from notifications.models import Notification


class NotificationTests(TestCase):

    def setUp(self):
        self.student = CustomUser.objects.create_user(
            username="notification_student",
            password="testpass123",
            role="student",
        )

        self.notification = Notification.objects.create(
            recipient=self.student,
            notification_type=Notification.MATERIAL,
            message="New course material available.",
        )

        self.client.login(
            username="notification_student",
            password="testpass123",
        )

    # -----------------------------------------
    # Normal POST marks notification as read
    # -----------------------------------------

    def test_user_can_mark_notification_as_read(self):
        response = self.client.post(
            reverse(
                "mark_notification_read",
                kwargs={
                    "notification_id": self.notification.id,
                },
            )
        )

        self.assertRedirects(
            response,
            reverse("notification_list"),
        )

        self.notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

    # -----------------------------------------
    # HTMX POST returns updated partial
    # -----------------------------------------

    def test_htmx_mark_notification_as_read(self):
        response = self.client.post(
            reverse(
                "mark_notification_read",
                kwargs={
                    "notification_id": self.notification.id,
                },
            ),
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

        self.assertContains(
            response,
            "Read",
        )