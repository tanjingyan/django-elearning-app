from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from courses.models import Course, Enrolment
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from courses.models import (
    Course,
    CourseBlock,
    CourseMaterial,
    Enrolment,
    Feedback,
)

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

    def test_feedback_rating_below_one_is_invalid(self):
        feedback = Feedback(
            student=self.student,
            course=self.course,
            rating=0,
            comment="Invalid rating.",
        )

        with self.assertRaises(ValidationError):
            feedback.full_clean()

    def test_feedback_rating_above_five_is_invalid(self):
        feedback = Feedback(
            student=self.student,
            course=self.course,
            rating=6,
            comment="Invalid rating.",
        )

        with self.assertRaises(ValidationError):
            feedback.full_clean()

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

    def test_course_material_teacher_is_derived_from_course(self):
        material = CourseMaterial.objects.create(
            course=self.course,
            title="Week 1 Notes",
            description="Testing course material relationship.",
            file="course_materials/week1.pdf",
        )

        self.assertEqual(
            material.course.teacher,
            self.teacher,
        )

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

        self.assertFalse(enrolment_exists)

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