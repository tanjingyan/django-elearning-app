from rest_framework import serializers
from accounts.models import CustomUser


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