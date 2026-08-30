from django.contrib import admin

from .models import (
    Course,
    CourseBlock,
    CourseMaterial,
    Enrolment,
    Feedback,
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "teacher",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "title",
        "teacher__username",
    )


@admin.register(Enrolment)
class EnrolmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "enrolled_at",
    )

    list_filter = (
        "enrolled_at",
        "course",
    )

    search_fields = (
        "student__username",
        "course__title",
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "rating",
        "created_at",
    )

    list_filter = (
        "rating",
        "created_at",
        "course",
    )

    search_fields = (
        "student__username",
        "course__title",
        "comment",
    )


@admin.register(CourseBlock)
class CourseBlockAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "course_teacher",
        "blocked_at",
    )

    list_filter = (
        "course",
        "blocked_at",
    )

    search_fields = (
        "student__username",
        "course__title",
        "course__teacher__username",
    )

    @admin.display(
        description="Teacher"
    )
    def course_teacher(self, obj):
        return obj.course.teacher


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "course_teacher",
        "uploaded_at",
    )

    list_filter = (
        "course",
        "uploaded_at",
    )

    search_fields = (
        "title",
        "course__title",
        "course__teacher__username",
    )

    @admin.display(
        description="Teacher"
    )
    def course_teacher(self, obj):
        return obj.course.teacher