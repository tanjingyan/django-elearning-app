from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser

from courses.models import (
    Course,
    CourseMaterial,
    Enrolment,
    Feedback,
)

from notifications.models import Notification

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

class ExtendedAPITests(APITestCase):

    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username="teacher_api",
            password="testpass123",
            role="teacher",
            email="teacher_api@example.com",
        )

        self.other_teacher = CustomUser.objects.create_user(
            username="teacher_other",
            password="testpass123",
            role="teacher",
            email="teacher_other@example.com",
        )

        self.student = CustomUser.objects.create_user(
            username="student_api",
            password="testpass123",
            role="student",
            email="student_api@example.com",
        )

        self.other_student = CustomUser.objects.create_user(
            username="student_other",
            password="testpass123",
            role="student",
            email="student_other@example.com",
        )

        self.course = Course.objects.create(
            teacher=self.teacher,
            title="API Testing Course",
            description="Course used for REST API testing.",
        )

        self.material = CourseMaterial.objects.create(
            course=self.course,
            title="Week 1 Notes",
            description="Testing material.",
            file="course_materials/week1.pdf",
        )

        self.enrolment = Enrolment.objects.create(
            student=self.student,
            course=self.course,
        )

        self.notification = Notification.objects.create(
            recipient=self.student,
            course=self.course,
            notification_type="material",
            message="New course material available.",
        )

    # -----------------------------------------
    # Course list
    # -----------------------------------------

    def test_authenticated_user_can_view_course_list(self):
        self.client.force_authenticate(
            user=self.student
        )

        url = reverse("api_course_list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data[0]["title"],
            "API Testing Course",
        )

    def test_unauthenticated_user_cannot_view_course_list(self):
        url = reverse("api_course_list")

        response = self.client.get(url)

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    # -----------------------------------------
    # Enrolments
    # -----------------------------------------

    def test_student_can_view_own_enrolments(self):
        self.client.force_authenticate(
            user=self.student
        )

        url = reverse(
            "api_current_user_enrolments"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["course"]["title"],
            "API Testing Course",
        )

    def test_student_can_enrol_in_course(self):
        second_course = Course.objects.create(
            teacher=self.teacher,
            title="Second API Course",
            description="Second course.",
        )

        self.client.force_authenticate(
            user=self.other_student
        )

        url = reverse(
            "api_course_enrol",
            kwargs={
                "pk": second_course.id,
            },
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Enrolment.objects.filter(
                student=self.other_student,
                course=second_course,
            ).exists()
        )

    def test_duplicate_enrolment_is_rejected(self):
        self.client.force_authenticate(
            user=self.student
        )

        url = reverse(
            "api_course_enrol",
            kwargs={
                "pk": self.course.id,
            },
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_teacher_cannot_enrol_in_course(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        url = reverse(
            "api_course_enrol",
            kwargs={
                "pk": self.course.id,
            },
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------
    # Course materials
    # -----------------------------------------

    def test_enrolled_student_can_view_course_materials(self):
        self.client.force_authenticate(
            user=self.student
        )

        url = reverse(
            "api_course_materials",
            kwargs={
                "pk": self.course.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data[0]["title"],
            "Week 1 Notes",
        )

    def test_non_enrolled_student_cannot_view_course_materials(self):
        self.client.force_authenticate(
            user=self.other_student
        )

        url = reverse(
            "api_course_materials",
            kwargs={
                "pk": self.course.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------
    # Course students
    # -----------------------------------------

    def test_course_teacher_can_view_enrolled_students(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        url = reverse(
            "api_course_students",
            kwargs={
                "pk": self.course.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data[0]["username"],
            "student_api",
        )

    def test_other_teacher_cannot_view_course_students(self):
        self.client.force_authenticate(
            user=self.other_teacher
        )

        url = reverse(
            "api_course_students",
            kwargs={
                "pk": self.course.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_student_cannot_view_course_student_list(self):
        self.client.force_authenticate(
            user=self.student
        )

        url = reverse(
            "api_course_students",
            kwargs={
                "pk": self.course.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # -----------------------------------------
    # Feedback
    # -----------------------------------------

    def test_enrolled_student_can_submit_feedback(self):
        self.client.force_authenticate(
            user=self.student
        )

        url = reverse(
            "api_course_feedback",
            kwargs={
                "pk": self.course.id,
            },
        )

        data = {
            "rating": 5,
            "comment": "Excellent course.",
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Feedback.objects.filter(
                student=self.student,
                course=self.course,
            ).exists()
        )

    def test_non_enrolled_student_cannot_submit_feedback(self):
        self.client.force_authenticate(
            user=self.other_student
        )

        url = reverse(
            "api_course_feedback",
            kwargs={
                "pk": self.course.id,
            },
        )

        data = {
            "rating": 4,
            "comment": "Test feedback.",
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_duplicate_feedback_is_rejected(self):
        Feedback.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            comment="First feedback.",
        )

        self.client.force_authenticate(
            user=self.student
        )

        url = reverse(
            "api_course_feedback",
            kwargs={
                "pk": self.course.id,
            },
        )

        data = {
            "rating": 4,
            "comment": "Second feedback.",
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_feedback_rating_is_rejected(self):
        self.client.force_authenticate(
            user=self.student
        )

        url = reverse(
            "api_course_feedback",
            kwargs={
                "pk": self.course.id,
            },
        )

        data = {
            "rating": 6,
            "comment": "Invalid rating.",
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # -----------------------------------------
    # Notifications
    # -----------------------------------------

    def test_student_only_sees_own_notifications(self):
        Notification.objects.create(
            recipient=self.other_student,
            course=self.course,
            notification_type="material",
            message="Other student's notification.",
        )

        self.client.force_authenticate(
            user=self.student
        )

        url = reverse(
            "api_current_user_notifications"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["message"],
            "New course material available.",
        )

    def test_notification_owner_can_mark_notification_read(self):
        self.client.force_authenticate(
            user=self.student
        )

        url = reverse(
            "api_notification_read",
            kwargs={
                "pk": self.notification.id,
            },
        )

        response = self.client.patch(
            url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

    def test_other_user_cannot_mark_notification_read(self):
        self.client.force_authenticate(
            user=self.other_student
        )

        url = reverse(
            "api_notification_read",
            kwargs={
                "pk": self.notification.id,
            },
        )

        response = self.client.patch(
            url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )