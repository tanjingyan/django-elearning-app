from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from courses.models import Course, Enrolment


class CourseTests(TestCase):

    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username="teacher1",
            password="testpass123",
            role="teacher",
        )

        self.student = CustomUser.objects.create_user(
            username="student1",
            password="testpass123",
            role="student",
        )

        self.course = Course.objects.create(
            teacher=self.teacher,
            title="Introduction to Python",
            description="Beginner Python course.",
        )

    def test_teacher_can_view_own_courses(self):
        self.client.login(
            username="teacher1",
            password="testpass123",
        )

        response = self.client.get(
            reverse("teacher_courses")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Introduction to Python",
        )

    def test_student_cannot_access_teacher_courses(self):
        self.client.login(
            username="student1",
            password="testpass123",
        )

        response = self.client.get(
            reverse("teacher_courses")
        )

        self.assertNotEqual(
            response.status_code,
            200,
        )

    def test_student_can_view_available_courses(self):
        self.client.login(
            username="student1",
            password="testpass123",
        )

        response = self.client.get(
            reverse("course_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Introduction to Python",
        )

    def test_student_can_enrol_in_course(self):
        self.client.login(
            username="student1",
            password="testpass123",
        )

        self.client.get(
            reverse(
                "enrol_course",
                kwargs={
                    "course_id": self.course.id,
                },
            )
        )

        enrolment_exists = Enrolment.objects.filter(
            student=self.student,
            course=self.course,
        ).exists()

        self.assertTrue(
            enrolment_exists
        )

    def test_teacher_cannot_enrol_as_student(self):
        self.client.login(
            username="teacher1",
            password="testpass123",
        )

        self.client.get(
            reverse(
                "enrol_course",
                kwargs={
                    "course_id": self.course.id,
                },
            )
        )

        enrolment_exists = Enrolment.objects.filter(
            student=self.teacher,
            course=self.course,
        ).exists()

        self.assertFalse(
            enrolment_exists
        )

    def test_course_teacher_can_view_course_detail(self):
        self.client.login(
            username="teacher1",
            password="testpass123",
        )

        response = self.client.get(
            reverse(
                "course_detail",
                kwargs={
                    "course_id": self.course.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )