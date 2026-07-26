from django.contrib import admin
from .models import Course, Enrolment, Feedback, CourseBlock, CourseMaterial


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "teacher",
        "created_at",
    )

    list_filter = (
        "teacher",
    )

    search_fields = (
        "title",
        "description",
    )


@admin.register(Enrolment)
class EnrolmentAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "course",
        "enrolled_at",
    )

    list_filter = (
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
        "teacher",
        "student",
        "course",
        "blocked_at",
    )

    list_filter = (
        "course",
    )

    search_fields = (
        "teacher__username",
        "student__username",
        "course__title",
    )

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "course",
        "teacher",
        "uploaded_at",
    )

    list_filter = (
        "course",
        "teacher",
    )

    search_fields = (
        "title",
        "course__title",
        "teacher__username",
    )