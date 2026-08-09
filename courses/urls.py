from django.urls import path

from . import views


urlpatterns = [

    path(
        "create/",
        views.create_course,
        name="create_course"
    ),

    path(
        "my-courses/",
        views.teacher_courses,
        name="teacher_courses"
    ),

    path(
        "",
        views.course_list,
        name="course_list"
    ),

    path(
        "<int:course_id>/",
        views.course_detail,
        name="course_detail"
    ),

    path(
        "<int:course_id>/enrol/",
        views.enrol_course,
        name="enrol_course"
    ),

    path(
        "<int:course_id>/feedback/create/",
        views.create_feedback,
        name="create_feedback"
    ),    

    path(
        "<int:course_id>/students/",
        views.course_students,
        name="course_students"
    ),

    path(
        "<int:course_id>/students/<int:student_id>/remove/",
        views.remove_student,
        name="remove_student"
    ),

    path(
        "<int:course_id>/students/<int:student_id>/block/",
        views.block_student,
        name="block_student"
    ),

    path(
        "<int:course_id>/materials/upload/",
        views.upload_material,
        name="upload_material"
    ),

    path(
        "<int:course_id>/edit/",
        views.edit_course,
        name="edit_course",
    ),

]