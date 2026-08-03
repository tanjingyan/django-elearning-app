from django.urls import path

from .views import (
    CurrentUserAPIView,
    UserDetailAPIView,
    UserListAPIView,
)

urlpatterns = [
    path(
        "users/me/",
        CurrentUserAPIView.as_view(),
        name="api_current_user",
    ),

    path(
        "users/",
        UserListAPIView.as_view(),
        name="api_user_list",
    ),

    path(
        "users/<int:pk>/",
        UserDetailAPIView.as_view(),
        name="api_user_detail",
    ),
]