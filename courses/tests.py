import tempfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import CustomUser
from courses.models import (
    Course,
    CourseBlock,
    CourseMaterial,
    Enrolment,
    Feedback,
)
from notifications.models import Notification


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

    # -----------------------------------------
    # Teacher can view own courses
    # -----------------------------------------

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

    # -----------------------------------------
    # Student cannot access teacher courses
    # -----------------------------------------

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

    # -----------------------------------------
    # Student can view available courses
    # -----------------------------------------

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

    # -----------------------------------------
    # Student can enrol
    # -----------------------------------------

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

    # -----------------------------------------
    # Teacher cannot enrol as student
    # -----------------------------------------

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

    # -----------------------------------------
    # Course teacher can view course detail
    # -----------------------------------------

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

    # -----------------------------------------
    # Teacher can create course
    # -----------------------------------------

    def test_teacher_can_create_course(self):
        self.client.login(
            username="teacher1",
            password="testpass123",
        )

        response = self.client.post(
            reverse("create_course"),
            {
                "title": "Web Development",
                "description": (
                    "A course about Django development."
                ),
            },
        )

        self.assertRedirects(
            response,
            reverse("teacher_courses"),
        )

        self.assertTrue(
            Course.objects.filter(
                teacher=self.teacher,
                title="Web Development",
            ).exists()
        )

    # -----------------------------------------
    # Enrolment creates teacher notification
    # -----------------------------------------

    def test_enrolment_notifies_course_teacher(self):
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

        notification = Notification.objects.filter(
            recipient=self.teacher,
            course=self.course,
            notification_type=Notification.ENROLMENT,
        ).first()

        self.assertIsNotNone(
            notification
        )

        self.assertIn(
            "student1",
            notification.message,
        )

        self.assertIn(
            "Introduction to Python",
            notification.message,
        )

    # -----------------------------------------
    # Teacher can block enrolled student
    # -----------------------------------------

    def test_teacher_can_block_student(self):
        Enrolment.objects.create(
            student=self.student,
            course=self.course,
        )

        self.client.login(
            username="teacher1",
            password="testpass123",
        )

        response = self.client.post(
            reverse(
                "block_student",
                kwargs={
                    "course_id": self.course.id,
                    "student_id": self.student.id,
                },
            )
        )

        self.assertRedirects(
            response,
            reverse(
                "course_students",
                kwargs={
                    "course_id": self.course.id,
                },
            ),
        )

        self.assertTrue(
            CourseBlock.objects.filter(
                student=self.student,
                course=self.course,
            ).exists()
        )

        self.assertFalse(
            Enrolment.objects.filter(
                student=self.student,
                course=self.course,
            ).exists()
        )

    # -----------------------------------------
    # Blocked student cannot re-enrol
    # -----------------------------------------

    def test_blocked_student_cannot_reenrol(self):
        CourseBlock.objects.create(
            student=self.student,
            course=self.course,
        )

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

        self.assertFalse(
            Enrolment.objects.filter(
                student=self.student,
                course=self.course,
            ).exists()
        )

    # -----------------------------------------
    # Material upload creates student
    # notification
    # -----------------------------------------

    def test_material_upload_notifies_enrolled_student(self):
        Enrolment.objects.create(
            student=self.student,
            course=self.course,
        )

        self.client.login(
            username="teacher1",
            password="testpass123",
        )

        test_file = SimpleUploadedFile(
            "week1_notes.txt",
            b"Week 1 course material.",
            content_type="text/plain",
        )

        with tempfile.TemporaryDirectory() as temp_media:
            with override_settings(
                MEDIA_ROOT=temp_media
            ):
                response = self.client.post(
                    reverse(
                        "upload_material",
                        kwargs={
                            "course_id": self.course.id,
                        },
                    ),
                    {
                        "title": "Week 1 Notes",
                        "description": (
                            "Introduction notes."
                        ),
                        "file": test_file,
                    },
                )

                self.assertRedirects(
                    response,
                    reverse(
                        "course_detail",
                        kwargs={
                            "course_id": self.course.id,
                        },
                    ),
                )

                self.assertTrue(
                    CourseMaterial.objects.filter(
                        course=self.course,
                        title="Week 1 Notes",
                    ).exists()
                )

                notification = (
                    Notification.objects.filter(
                        recipient=self.student,
                        course=self.course,
                        notification_type=(
                            Notification.MATERIAL
                        ),
                    ).first()
                )

                self.assertIsNotNone(
                    notification
                )

                self.assertIn(
                    "Week 1 Notes",
                    notification.message,
                )


class CourseModelTests(TestCase):

    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username="teacher_model",
            password="testpass123",
            role="teacher",
        )

        self.student = CustomUser.objects.create_user(
            username="student_model",
            password="testpass123",
            role="student",
        )

        self.course = Course.objects.create(
            teacher=self.teacher,
            title="Database Testing Course",
            description="Course used for model tests.",
        )

    # -----------------------------------------
    # Duplicate enrolment constraint
    # -----------------------------------------

    def test_duplicate_enrolment_is_not_allowed(self):
        Enrolment.objects.create(
            student=self.student,
            course=self.course,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Enrolment.objects.create(
                    student=self.student,
                    course=self.course,
                )

    # -----------------------------------------
    # Duplicate feedback constraint
    # -----------------------------------------

    def test_duplicate_feedback_is_not_allowed(self):
        Feedback.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            comment="Excellent course.",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Feedback.objects.create(
                    student=self.student,
                    course=self.course,
                    rating=4,
                    comment="Second feedback.",
                )

    # -----------------------------------------
    # Feedback lower rating boundary
    # -----------------------------------------

    def test_feedback_rating_below_one_is_invalid(self):
        feedback = Feedback(
            student=self.student,
            course=self.course,
            rating=0,
            comment="Invalid rating.",
        )

        with self.assertRaises(ValidationError):
            feedback.full_clean()

    # -----------------------------------------
    # Feedback upper rating boundary
    # -----------------------------------------

    def test_feedback_rating_above_five_is_invalid(self):
        feedback = Feedback(
            student=self.student,
            course=self.course,
            rating=6,
            comment="Invalid rating.",
        )

        with self.assertRaises(ValidationError):
            feedback.full_clean()

    # -----------------------------------------
    # Duplicate course block constraint
    # -----------------------------------------

    def test_duplicate_course_block_is_not_allowed(self):
        CourseBlock.objects.create(
            student=self.student,
            course=self.course,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CourseBlock.objects.create(
                    student=self.student,
                    course=self.course,
                )

    # -----------------------------------------
    # Course material teacher relationship
    # -----------------------------------------

    def test_course_material_teacher_is_derived_from_course(self):
        material = CourseMaterial.objects.create(
            course=self.course,
            title="Week 1 Notes",
            description=(
                "Testing course material relationship."
            ),
            file="course_materials/week1.pdf",
        )

        self.assertEqual(
            material.course.teacher,
            self.teacher,
        )

    # -----------------------------------------
    # Course deletion cascades to enrolments
    # -----------------------------------------

    def test_deleting_course_removes_enrolments(self):
        Enrolment.objects.create(
            student=self.student,
            course=self.course,
        )

        course_id = self.course.id

        self.course.delete()

        enrolment_exists = Enrolment.objects.filter(
            course_id=course_id,
        ).exists()

        self.assertFalse(
            enrolment_exists
        )

    # -----------------------------------------
    # Student-enrolment relationship
    # -----------------------------------------

    def test_student_enrolment_relationship_works(self):
        Enrolment.objects.create(
            student=self.student,
            course=self.course,
        )

        self.assertEqual(
            self.student.enrolments.count(),
            1,
        )

        self.assertEqual(
            self.student.enrolments.first().course,
            self.course,
        )

    # -----------------------------------------
    # Course-feedback relationship
    # -----------------------------------------

    def test_course_feedback_relationship_works(self):
        feedback = Feedback.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            comment="Very useful.",
        )

        self.assertEqual(
            self.course.feedback.count(),
            1,
        )

        self.assertEqual(
            self.course.feedback.first(),
            feedback,
        )