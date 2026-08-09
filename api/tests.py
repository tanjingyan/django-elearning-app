from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser


class UserAPITests(APITestCase):

    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username="teacher1",
            password="testpass123",
            role="teacher",
            email="teacher@example.com",
        )

        self.student1 = CustomUser.objects.create_user(
            username="student1",
            password="testpass123",
            role="student",
            email="student1@example.com",
        )

        self.student2 = CustomUser.objects.create_user(
            username="student2",
            password="testpass123",
            role="student",
            email="student2@example.com",
        )


    # -----------------------------------------
    # Unauthenticated user
    # -----------------------------------------

    def test_unauthenticated_user_cannot_access_current_user_api(self):
        url = reverse("api_current_user")

        response = self.client.get(url)

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )


    # -----------------------------------------
    # Student can access own data
    # -----------------------------------------

    def test_student_can_access_own_data(self):
        self.client.force_authenticate(
            user=self.student1
        )

        url = reverse(
            "api_user_detail",
            kwargs={
                "pk": self.student1.id
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["username"],
            "student1",
        )


    # -----------------------------------------
    # Student cannot access another user
    # -----------------------------------------

    def test_student_cannot_access_other_student_data(self):
        self.client.force_authenticate(
            user=self.student1
        )

        url = reverse(
            "api_user_detail",
            kwargs={
                "pk": self.student2.id
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


    # -----------------------------------------
    # Student cannot list all users
    # -----------------------------------------

    def test_student_cannot_view_user_list(self):
        self.client.force_authenticate(
            user=self.student1
        )

        url = reverse("api_user_list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


    # -----------------------------------------
    # Teacher can list users
    # -----------------------------------------

    def test_teacher_can_view_user_list(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        url = reverse("api_user_list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            3,
        )


    # -----------------------------------------
    # Teacher can access student data
    # -----------------------------------------

    def test_teacher_can_access_student_data(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        url = reverse(
            "api_user_detail",
            kwargs={
                "pk": self.student1.id
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["username"],
            "student1",
        )


    # -----------------------------------------
    # Current user endpoint
    # -----------------------------------------

    def test_current_user_api_returns_logged_in_user(self):
        self.client.force_authenticate(
            user=self.student1
        )

        url = reverse("api_current_user")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["username"],
            "student1",
        )


    # -----------------------------------------
    # PATCH current user
    # -----------------------------------------

    def test_user_can_patch_own_profile(self):
        self.client.force_authenticate(
            user=self.student1
        )

        url = reverse("api_current_user")

        data = {
            "bio": "Updated using the REST API.",
            "first_name": "Student",
        }

        response = self.client.patch(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.student1.refresh_from_db()

        self.assertEqual(
            self.student1.bio,
            "Updated using the REST API.",
        )

        self.assertEqual(
            self.student1.first_name,
            "Student",
        )


    # -----------------------------------------
    # Student cannot change own role
    # -----------------------------------------

    def test_student_cannot_change_role_using_api(self):
        self.client.force_authenticate(
            user=self.student1
        )

        url = reverse("api_current_user")

        data = {
            "role": "teacher",
        }

        response = self.client.patch(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.student1.refresh_from_db()

        self.assertEqual(
            self.student1.role,
            "student",
        )