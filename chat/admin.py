from django.contrib import admin

from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        "sender",
        "course",
        "created_at",
    )

    list_filter = (
        "course",
        "created_at",
    )

    search_fields = (
        "sender__username",
        "course__title",
        "message",
    )

    ordering = (
        "-created_at",
    )