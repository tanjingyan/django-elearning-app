from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser, StatusUpdate


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

    # -----------------------------------------
    # Student login
    # -----------------------------------------

    def test_student_can_login(self):
        login_successful = self.client.login(
            username="student1",
            password="testpass123",
        )

        self.assertTrue(
            login_successful
        )

    # -----------------------------------------
    # Teacher login
    # -----------------------------------------

    def test_teacher_can_login(self):
        login_successful = self.client.login(
            username="teacher1",
            password="testpass123",
        )

        self.assertTrue(
            login_successful
        )

    # -----------------------------------------
    # Student cannot access teacher dashboard
    # -----------------------------------------

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

    # -----------------------------------------
    # Teacher can access teacher dashboard
    # -----------------------------------------

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

    # -----------------------------------------
    # Student profile page
    # -----------------------------------------

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

    # -----------------------------------------
    # Account registration
    # -----------------------------------------

    def test_student_can_register_account(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newstudent",
                "first_name": "New",
                "last_name": "Student",
                "email": "newstudent@example.com",
                "role": "student",
                "bio": "Test account",
                "password1": "StrongTestPass123!",
                "password2": "StrongTestPass123!",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        user = CustomUser.objects.get(
            username="newstudent"
        )

        self.assertEqual(
            user.role,
            "student",
        )

        # Confirms that Django hashed the password
        self.assertTrue(
            user.check_password(
                "StrongTestPass123!"
            )
        )

    # -----------------------------------------
    # Logout
    # -----------------------------------------

    def test_authenticated_user_can_logout(self):
        self.client.login(
            username="student1",
            password="testpass123",
        )

        response = self.client.get(
            reverse("logout")
        )

        self.assertRedirects(
            response,
            reverse("login"),
        )

        # Protected page should no longer be
        # accessible after logout
        response = self.client.get(
            reverse("student_dashboard")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    # -----------------------------------------
    # Teacher user search
    # -----------------------------------------

    def test_teacher_can_search_for_student(self):
        self.client.login(
            username="teacher1",
            password="testpass123",
        )

        response = self.client.get(
            reverse("search_users"),
            {
                "q": "student1",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "student1",
        )

    # -----------------------------------------
    # Status update
    # -----------------------------------------

    def test_student_can_create_status_update(self):
        self.client.login(
            username="student1",
            password="testpass123",
        )

        response = self.client.post(
            reverse("create_status"),
            {
                "content": "Studying Django today.",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            StatusUpdate.objects.filter(
                user=self.student,
                content="Studying Django today.",
            ).exists()
        )

    # -----------------------------------------
    # Teacher profile page
    # -----------------------------------------

    def test_teacher_profile_is_accessible(self):
        self.client.login(
            username="teacher1",
            password="testpass123",
        )

        response = self.client.get(
            reverse(
                "profile",
                kwargs={
                    "username": self.teacher.username,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )