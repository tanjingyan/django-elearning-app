from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course, Enrolment

from .models import ChatMessage


@login_required
def course_chat(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
    )

    is_teacher = (
        request.user.role == "teacher"
        and course.teacher == request.user
    )

    is_enrolled_student = (
        request.user.role == "student"
        and Enrolment.objects.filter(
            course=course,
            student=request.user,
        ).exists()
    )

    if not is_teacher and not is_enrolled_student:
        if request.user.role == "teacher":
            return redirect("teacher_courses")

        return redirect("course_list")

    messages = ChatMessage.objects.filter(
        course=course,
    ).select_related(
        "sender",
    ).order_by(
        "created_at",
    )

    return render(
        request,
        "chat/course_chat.html",
        {
            "course": course,
            "messages": messages,
        },
    )