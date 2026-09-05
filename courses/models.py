from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from accounts.models import CustomUser


class Course(models.Model):

    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="courses_created",
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to="course_images/",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    CATEGORY_CHOICES = [
        ("computer_science", "Computer Science"),
        ("programming", "Programming"),
        ("web_development", "Web Development"),
        ("databases", "Databases"),
        ("artificial_intelligence", "Artificial Intelligence"),
        ("cybersecurity", "Cybersecurity"),
        ("software_engineering", "Software Engineering"),
        ("other", "Other"),
    ]
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="other",
    )


class Enrolment(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="enrolments",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrolments",
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_enrolment",
            ),
        ]

        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


class Feedback(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="feedback_given",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="feedback",
    )

    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    comment = models.TextField(
        max_length=1000,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course_feedback",
            ),

            models.CheckConstraint(
                condition=models.Q(
                    rating__gte=1,
                    rating__lte=5,
                ),
                name="feedback_rating_between_1_and_5",
            ),
        ]

        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


class CourseBlock(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="course_blocks_received",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="blocked_students",
    )

    blocked_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_course_block",
            ),
        ]

        ordering = ["-blocked_at"]

    def __str__(self):
        return (
            f"{self.student.username} "
            f"blocked from {self.course.title}"
        )


class CourseMaterial(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="materials",
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    file = models.FileField(
        upload_to="course_materials/",
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title