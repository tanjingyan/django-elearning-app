from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.home_redirect,
        name="home",
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "student/dashboard/",
        views.student_dashboard,
        name="student_dashboard"
    ),

    path(
        "teacher/dashboard/",
        views.teacher_dashboard,
        name="teacher_dashboard"
    ),

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile",
    ),

    path(
        "profile/<str:username>/",
        views.profile,
        name="profile"
    ),

    path(
        "status/create/",
        views.create_status,
        name="create_status"
    ),

    path(
        "search-users/",
        views.search_users,
        name="search_users"
    ),
    
]