from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "recipient",
        "course",
        "message",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "course",
    )

    search_fields = (
        "recipient__username",
        "message",
        "course__title",
    )

    ordering = (
        "-created_at",
    )