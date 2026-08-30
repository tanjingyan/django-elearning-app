from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, Enrolment, Feedback, CourseBlock, CourseMaterial
from .forms import CourseForm, FeedbackForm, CourseMaterialForm
from accounts.models import CustomUser
from notifications.tasks import (
    create_enrolment_notification,
    create_material_notifications,
)

@login_required
def create_course(request):
    if request.user.role != "teacher":
        return redirect("student_dashboard")

    if request.method == "POST":
        form = CourseForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()

            return redirect("teacher_courses")

    else:
        form = CourseForm()

    return render(
        request,
        "courses/create_course.html",
        {
            "form": form,
        },
    )

@login_required
def teacher_courses(request):
    if request.user.role != "teacher":
        return redirect("student_dashboard")

    courses = Course.objects.filter(
        teacher=request.user
    ).order_by("-created_at")

    return render(
        request,
        "courses/teacher_courses.html",
        {
            "courses": courses,
        },
    )

@login_required
def course_list(request):

    courses = Course.objects.all()

    return render(
        request,
        "courses/course_list.html",
        {
            "courses": courses
        }
    )

@login_required
def course_detail(request, course_id):

    course = Course.objects.get(
        id=course_id
    )

    is_enrolled = Enrolment.objects.filter(
        student=request.user,
        course=course
    ).exists()

    feedback_list = course.feedback.all()

    has_feedback = Feedback.objects.filter(
        student=request.user,
        course=course
    ).exists()

    materials = course.materials.all().order_by(
        "-uploaded_at"
    )

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "is_enrolled": is_enrolled,
            "feedback_list": feedback_list,
            "has_feedback": has_feedback,
            "materials": materials,
        }
    )

@login_required
def enrol_course(request, course_id):

    if request.user.role != "student":
        return redirect("teacher_dashboard")

    course = Course.objects.get(id=course_id)

    is_blocked = CourseBlock.objects.filter(
        student=request.user,
        course=course
    ).exists()

    if is_blocked:
        return redirect(
            "course_detail",
            course_id=course.id
        )

    enrolment, created = Enrolment.objects.get_or_create(
        student=request.user,
        course=course
    )

    if created:
        create_enrolment_notification.delay(
            enrolment.id
        )

    return redirect(
        "course_detail",
        course_id=course.id
    )

@login_required
def create_feedback(request, course_id):

    if request.user.role != "student":
        return redirect("teacher_dashboard")

    course = Course.objects.get(
        id=course_id
    )

    # Check whether student is enrolled
    is_enrolled = Enrolment.objects.filter(
        student=request.user,
        course=course
    ).exists()

    if not is_enrolled:
        return redirect(
            "course_detail",
            course_id=course.id
        )

    # Check if student already submitted feedback
    existing_feedback = Feedback.objects.filter(
        student=request.user,
        course=course
    ).first()

    if existing_feedback:
        return redirect(
            "course_detail",
            course_id=course.id
        )

    if request.method == "POST":

        form = FeedbackForm(
            request.POST
        )

        if form.is_valid():

            feedback = form.save(
                commit=False
            )

            feedback.student = request.user
            feedback.course = course

            feedback.save()

            return redirect(
                "course_detail",
                course_id=course.id
            )

    else:

        form = FeedbackForm()

    return render(
        request,
        "courses/create_feedback.html",
        {
            "form": form,
            "course": course,
        }
    )

@login_required
def course_students(request, course_id):

    if request.user.role != "teacher":
        return redirect("student_dashboard")

    course = Course.objects.get(
        id=course_id
    )

    if course.teacher != request.user:
        return redirect("teacher_courses")

    enrolments = Enrolment.objects.filter(
        course=course
    ).select_related(
        "student"
    )

    return render(
        request,
        "courses/course_students.html",
        {
            "course": course,
            "enrolments": enrolments,
        }
    )

@login_required
def remove_student(request, course_id, student_id):

    if request.user.role != "teacher":
        return redirect("student_dashboard")

    if request.method != "POST":
        return redirect(
            "course_students",
            course_id=course_id
        )

    course = Course.objects.get(
        id=course_id
    )

    if course.teacher != request.user:
        return redirect("teacher_courses")

    Enrolment.objects.filter(
        course=course,
        student_id=student_id
    ).delete()

    return redirect(
        "course_students",
        course_id=course.id
    )

@login_required
def block_student(request, course_id, student_id):

    if request.user.role != "teacher":
        return redirect("student_dashboard")

    if request.method != "POST":
        return redirect(
            "course_students",
            course_id=course_id,
        )

    course = Course.objects.get(
        id=course_id
    )

    if course.teacher != request.user:
        return redirect("teacher_courses")

    student = CustomUser.objects.get(
        id=student_id
    )

    CourseBlock.objects.get_or_create(
        student=student,
        course=course,
    )

    Enrolment.objects.filter(
        course=course,
        student=student,
    ).delete()

    return redirect(
        "course_students",
        course_id=course.id,
    )


@login_required
def upload_material(request, course_id):

    # Only teachers can upload materials
    if request.user.role != "teacher":
        return redirect("student_dashboard")

    course = get_object_or_404(
        Course,
        id=course_id,
    )

    # Only the teacher who owns the course
    # can upload material to it
    if course.teacher != request.user:
        return redirect("teacher_courses")

    if request.method == "POST":

        form = CourseMaterialForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            material = form.save(
                commit=False
            )

            material.course = course
            material.save()

            # Create student notifications
            # asynchronously using Celery
            create_material_notifications.delay(
                material.id
            )

            return redirect(
                "course_detail",
                course_id=course.id,
            )

    else:
        form = CourseMaterialForm()

    return render(
        request,
        "courses/upload_material.html",
        {
            "form": form,
            "course": course,
        },
    )

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
    )

    if request.user.role != "teacher":
        return redirect("student_dashboard")

    if course.teacher != request.user:
        return redirect("teacher_courses")

    if request.method == "POST":
        form = CourseForm(
            request.POST,
            request.FILES,
            instance=course,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "course_detail",
                course_id=course.id,
            )

    else:
        form = CourseForm(
            instance=course,
        )

    return render(
        request,
        "courses/edit_course.html",
        {
            "form": form,
            "course": course,
        },
    )