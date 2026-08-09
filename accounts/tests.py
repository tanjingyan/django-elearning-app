from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class AccountTests(TestCase):

    def setUp(self):
        self.student = CustomUser.objects.create_user(
            username="student1",
            password="testpass123",
            role="student",
            email="student1@example.com",
        )

        self.teacher = CustomUser.objects.create_user(
            username="teacher1",
            password="testpass123",
            role="teacher",
            email="teacher1@example.com",
        )

    def test_student_can_login(self):
        login_successful = self.client.login(
            username="student1",
            password="testpass123",
        )

        self.assertTrue(login_successful)

    def test_teacher_can_login(self):
        login_successful = self.client.login(
            username="teacher1",
            password="testpass123",
        )

        self.assertTrue(login_successful)

    def test_student_cannot_access_teacher_dashboard(self):
        self.client.login(
            username="student1",
            password="testpass123",
        )

        response = self.client.get(
            reverse("teacher_dashboard")
        )

        self.assertNotEqual(
            response.status_code,
            200,
        )

    def test_teacher_can_access_teacher_dashboard(self):
        self.client.login(
            username="teacher1",
            password="testpass123",
        )

        response = self.client.get(
            reverse("teacher_dashboard")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_profile_page_is_accessible(self):
        self.client.login(
            username="student1",
            password="testpass123",
        )

        response = self.client.get(
            reverse(
                "profile",
                kwargs={
                    "username": self.student.username,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )