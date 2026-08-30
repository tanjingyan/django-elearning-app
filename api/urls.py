from django.urls import path

from .views import (
    CourseDetailAPIView,
    CourseEnrolAPIView,
    CourseFeedbackAPIView,
    CourseListAPIView,
    CourseMaterialsAPIView,
    CourseStudentsAPIView,
    CurrentUserAPIView,
    CurrentUserEnrolmentsAPIView,
    CurrentUserNotificationsAPIView,
    NotificationReadAPIView,
    UserDetailAPIView,
    UserListAPIView,
)


urlpatterns = [
    # ========================================================
    # CURRENT USER
    # ========================================================

    path(
        "users/me/",
        CurrentUserAPIView.as_view(),
        name="api_current_user",
    ),

    path(
        "users/me/enrolments/",
        CurrentUserEnrolmentsAPIView.as_view(),
        name="api_current_user_enrolments",
    ),

    path(
        "users/me/notifications/",
        CurrentUserNotificationsAPIView.as_view(),
        name="api_current_user_notifications",
    ),

    # ========================================================
    # USERS
    # ========================================================

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

    # ========================================================
    # COURSES
    # ========================================================

    path(
        "courses/",
        CourseListAPIView.as_view(),
        name="api_course_list",
    ),

    path(
        "courses/<int:pk>/",
        CourseDetailAPIView.as_view(),
        name="api_course_detail",
    ),

    path(
        "courses/<int:pk>/materials/",
        CourseMaterialsAPIView.as_view(),
        name="api_course_materials",
    ),

    path(
        "courses/<int:pk>/students/",
        CourseStudentsAPIView.as_view(),
        name="api_course_students",
    ),

    path(
        "courses/<int:pk>/enrol/",
        CourseEnrolAPIView.as_view(),
        name="api_course_enrol",
    ),

    path(
        "courses/<int:pk>/feedback/",
        CourseFeedbackAPIView.as_view(),
        name="api_course_feedback",
    ),

    # ========================================================
    # NOTIFICATIONS
    # ========================================================

    path(
        "notifications/<int:pk>/read/",
        NotificationReadAPIView.as_view(),
        name="api_notification_read",
    ),
]