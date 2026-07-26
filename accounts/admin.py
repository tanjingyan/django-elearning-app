from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StatusUpdate


@admin.register(CustomUser)

class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "role",
                    "profile_picture",
                    "bio",
                )
            },
        ),
    )

admin.site.register(StatusUpdate)