from rest_framework import serializers

from accounts.models import CustomUser
from courses.models import (
    Course,
    CourseMaterial,
    Enrolment,
    Feedback,
)
from notifications.models import Notification


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser

        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "profile_picture",
            "bio",
        )

        read_only_fields = (
            "id",
            "username",
            "role",
        )


class CourseSerializer(serializers.ModelSerializer):
    teacher_username = serializers.CharField(
        source="teacher.username",
        read_only=True,
    )

    category_display = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    enrolment_count = serializers.SerializerMethodField()

    class Meta:
        model = Course

        fields = (
            "id",
            "title",
            "description",
            "category",
            "category_display",
            "image",
            "teacher_username",
            "created_at",
            "enrolment_count",
        )

        read_only_fields = fields

    def get_enrolment_count(self, obj):
        return obj.enrolments.count()


class CourseMaterialSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source="course.title",
        read_only=True,
    )

    class Meta:
        model = CourseMaterial

        fields = (
            "id",
            "course",
            "course_title",
            "title",
            "description",
            "file",
            "uploaded_at",
        )

        read_only_fields = fields


class EnrolmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(
        read_only=True,
    )

    class Meta:
        model = Enrolment

        fields = (
            "id",
            "course",
            "enrolled_at",
        )

        read_only_fields = fields


class FeedbackSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(
        source="student.username",
        read_only=True,
    )

    class Meta:
        model = Feedback

        fields = (
            "id",
            "student_username",
            "course",
            "rating",
            "comment",
            "created_at",
        )

        read_only_fields = (
            "id",
            "student_username",
            "course",
            "created_at",
        )


class NotificationSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source="course.title",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Notification

        fields = (
            "id",
            "course",
            "course_title",
            "notification_type",
            "message",
            "is_read",
            "created_at",
        )

        read_only_fields = (
            "id",
            "course",
            "course_title",
            "notification_type",
            "message",
            "created_at",
        )