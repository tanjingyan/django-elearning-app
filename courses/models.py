from django.db import models
from accounts.models import CustomUser


class Course(models.Model):

    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="courses_created"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

class Enrolment(models.Model):

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="enrolments"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrolments"
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "student",
            "course",
        )

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class Feedback(models.Model):

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="feedback_given"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="feedback"
    )

    rating = models.PositiveIntegerField()

    comment = models.TextField(
        max_length=1000
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "student",
            "course",
        )

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class CourseBlock(models.Model):

    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="course_blocks_created"
    )

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="course_blocks_received"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="blocked_students"
    )

    blocked_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "student",
            "course",
        )

    def __str__(self):
        return (
            f"{self.student.username} "
            f"blocked from {self.course.title}"
        )

class CourseMaterial(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="materials"
    )

    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="uploaded_materials"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    file = models.FileField(
        upload_to="course_materials/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title