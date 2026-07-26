from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Course, Enrolment, Feedback, CourseBlock, CourseMaterial
from .forms import CourseForm, FeedbackForm, CourseMaterialForm
from accounts.models import CustomUser
from notifications.models import Notification

@login_required
def create_course(request):

    # Only teachers can create courses
    if request.user.role != "teacher":
        return redirect("student_dashboard")

    if request.method == "POST":

        form = CourseForm(request.POST)

        if form.is_valid():

            course = form.save(
                commit=False
            )

            # Automatically assign logged-in teacher
            course.teacher = request.user

            course.save()

            return redirect(
                "teacher_courses"
            )

    else:

        form = CourseForm()

    return render(
        request,
        "courses/create_course.html",
        {
            "form": form
        }
    )

@login_required
def teacher_courses(request):

    # Only teachers can access this page
    if request.user.role != "teacher":
        return redirect("student_dashboard")

    courses = request.user.courses_created.all()

    return render(
        request,
        "courses/teacher_courses.html",
        {
            "courses": courses
        }
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

    course = Course.objects.get(
        id=course_id
    )

    is_blocked = CourseBlock.objects.filter(
        student=request.user,
        course=course
    ).exists()

    if is_blocked:
        return redirect(
            "course_detail",
            course_id=course.id
        )

    Enrolment.objects.get_or_create(
        student=request.user,
        course=course
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
            course_id=course_id
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
        teacher=request.user,
        student=student,
        course=course
    )

    Enrolment.objects.filter(
        course=course,
        student=student
    ).delete()

    return redirect(
        "course_students",
        course_id=course.id
    )

@login_required
def upload_material(request, course_id):

    if request.user.role != "teacher":
        return redirect("student_dashboard")

    course = Course.objects.get(
        id=course_id
    )

    # Make sure the logged-in teacher owns this course
    if course.teacher != request.user:
        return redirect("teacher_courses")

    if request.method == "POST":

        form = CourseMaterialForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            # Save the uploaded material
            material = form.save(
                commit=False
            )

            material.course = course
            material.teacher = request.user

            material.save()


            # Find all students enrolled in this course
            enrolments = Enrolment.objects.filter(
                course=course
            )


            # Create a notification for each enrolled student
            for enrolment in enrolments:

                Notification.objects.create(

                    recipient=enrolment.student,

                    course=course,

                    message=(
                        f'New material "{material.title}" '
                        f'has been added to '
                        f'"{course.title}".'
                    )

                )


            return redirect(
                "course_detail",
                course_id=course.id
            )

    else:

        form = CourseMaterialForm()


    return render(
        request,
        "courses/upload_material.html",
        {
            "form": form,
            "course": course,
        }
    )