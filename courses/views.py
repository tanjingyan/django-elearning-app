from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    Course,
    Enrolment,
    Feedback,
    CourseBlock,
    CourseMaterial,
)

from .forms import (
    CourseForm,
    FeedbackForm,
    CourseMaterialForm,
)

from accounts.models import CustomUser

from notifications.tasks import (
    create_enrolment_notification,
    create_material_notifications,
)

from chat.models import ChatMessage

from django.db.models import Avg

# =========================================================
# CREATE COURSE
# =========================================================

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

            course = form.save(
                commit=False
            )

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
            "form": form,
        },
    )



# =========================================================
# TEACHER COURSES
# =========================================================

@login_required
def teacher_courses(request):

    if request.user.role != "teacher":
        return redirect(
            "student_dashboard"
        )


    courses = (
        Course.objects
        .filter(
            teacher=request.user
        )
        .order_by(
            "-created_at"
        )
    )


    return render(
        request,
        "courses/teacher_courses.html",
        {
            "courses": courses,
        },
    )



# =========================================================
# COURSE LIST
# =========================================================

@login_required
def course_list(request):

    courses = (
        Course.objects
        .select_related("teacher")
        .order_by("-created_at")
    )

    enrolled_course_ids = set()

    if request.user.role == "student":

        enrolled_course_ids = set(
            Enrolment.objects
            .filter(student=request.user)
            .values_list(
                "course_id",
                flat=True,
            )
        )


    course_cards = []

    for course in courses:

        enrolment_count = (
            Enrolment.objects
            .filter(course=course)
            .count()
        )

        feedback_data = (
            Feedback.objects
            .filter(course=course)
            .aggregate(
                average_rating=Avg("rating")
            )
        )

        rating_count = (
            Feedback.objects
            .filter(course=course)
            .count()
        )

        course_cards.append(
            {
                "course": course,

                "enrolment_count":
                    enrolment_count,

                "average_rating":
                    feedback_data[
                        "average_rating"
                    ],

                "rating_count":
                    rating_count,

                "is_enrolled":
                    course.id
                    in enrolled_course_ids,
            }
        )


    categories = Course.CATEGORY_CHOICES


    return render(
        request,
        "courses/course_list.html",
        {
            "course_cards":
                course_cards,

            "categories":
                categories,
        },
    )



# =========================================================
# COURSE DETAIL
# =========================================================

@login_required
def course_detail(request, course_id):

    course = get_object_or_404(
        Course.objects.select_related(
            "teacher"
        ),
        id=course_id,
    )


    # ---------------------------------------------------------
    # DEFAULT STUDENT STATES
    # ---------------------------------------------------------

    is_enrolled = False
    is_blocked = False
    has_feedback = False



    # ---------------------------------------------------------
    # STUDENT ACCESS
    # ---------------------------------------------------------

    if request.user.role == "student":

        is_blocked = (
            CourseBlock.objects
            .filter(
                student=request.user,
                course=course,
            )
            .exists()
        )


        is_enrolled = (
            Enrolment.objects
            .filter(
                student=request.user,
                course=course,
            )
            .exists()
        )


        has_feedback = (
            Feedback.objects
            .filter(
                student=request.user,
                course=course,
            )
            .exists()
        )



        # -----------------------------------------------------
        # REMEMBER LAST VIEWED ENROLLED COURSE
        # -----------------------------------------------------

        if (
            is_enrolled
            and not is_blocked
        ):

            request.session[
                "last_viewed_course_id"
            ] = course.id



    # ---------------------------------------------------------
    # COURSE MATERIALS
    # ---------------------------------------------------------

    materials = (
        CourseMaterial.objects.none()
    )


    if (
        request.user == course.teacher
        or (
            is_enrolled
            and not is_blocked
        )
    ):

        materials = (
            CourseMaterial.objects
            .filter(
                course=course
            )
            .order_by(
                "-uploaded_at"
            )
        )



    # ---------------------------------------------------------
    # COURSE FEEDBACK
    # ---------------------------------------------------------

    feedback_list = (
        Feedback.objects
        .filter(
            course=course
        )
        .select_related(
            "student"
        )
        .order_by(
            "-created_at"
        )
    )



    # ---------------------------------------------------------
    # TEACHER STUDENT PREVIEW
    # ---------------------------------------------------------

    student_preview = []

    student_count = 0


    if request.user == course.teacher:

        course_enrolments = (
            Enrolment.objects
            .filter(
                course=course
            )
            .select_related(
                "student"
            )
            .order_by(
                "-enrolled_at"
            )
        )


        student_count = (
            course_enrolments.count()
        )


        student_preview = (
            course_enrolments[:3]
        )



    # ---------------------------------------------------------
    # RECENT LIVE DISCUSSION MESSAGES
    # ---------------------------------------------------------

    recent_chat_messages = (
        ChatMessage.objects
        .filter(
            course=course
        )
        .select_related(
            "sender"
        )
        .order_by(
            "-created_at"
        )[:2]
    )



    # ---------------------------------------------------------
    # RENDER COURSE DETAIL
    # ---------------------------------------------------------

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,

            "is_enrolled": is_enrolled,
            "is_blocked": is_blocked,

            "materials": materials,

            "feedback_list": feedback_list,
            "has_feedback": has_feedback,

            "student_preview":
                student_preview,

            "student_count":
                student_count,

            "recent_chat_messages":
                recent_chat_messages,
        },
    )



# =========================================================
# ENROL COURSE
# =========================================================

@login_required
def enrol_course(request, course_id):

    if request.user.role != "student":

        return redirect(
            "teacher_dashboard"
        )


    course = get_object_or_404(
        Course,
        id=course_id,
    )



    # ---------------------------------------------------------
    # CHECK WHETHER STUDENT IS BLOCKED
    # ---------------------------------------------------------

    is_blocked = (
        CourseBlock.objects
        .filter(
            student=request.user,
            course=course,
        )
        .exists()
    )


    if is_blocked:

        return redirect(
            "course_detail",
            course_id=course.id,
        )



    # ---------------------------------------------------------
    # CREATE ENROLMENT
    # ---------------------------------------------------------

    enrolment, created = (
        Enrolment.objects
        .get_or_create(
            student=request.user,
            course=course,
        )
    )



    # ---------------------------------------------------------
    # SEND TEACHER NOTIFICATION
    # ---------------------------------------------------------

    if created:

        create_enrolment_notification.delay(
            enrolment.id
        )



    return redirect(
        "course_detail",
        course_id=course.id,
    )



# =========================================================
# CREATE FEEDBACK
# =========================================================

@login_required
def create_feedback(request, course_id):

    if request.user.role != "student":

        return redirect(
            "teacher_dashboard"
        )


    course = get_object_or_404(
        Course,
        id=course_id,
    )



    # ---------------------------------------------------------
    # CHECK WHETHER STUDENT IS ENROLLED
    # ---------------------------------------------------------

    is_enrolled = (
        Enrolment.objects
        .filter(
            student=request.user,
            course=course,
        )
        .exists()
    )


    if not is_enrolled:

        return redirect(
            "course_detail",
            course_id=course.id,
        )



    # ---------------------------------------------------------
    # CHECK WHETHER STUDENT IS BLOCKED
    # ---------------------------------------------------------

    is_blocked = (
        CourseBlock.objects
        .filter(
            student=request.user,
            course=course,
        )
        .exists()
    )


    if is_blocked:

        return redirect(
            "course_detail",
            course_id=course.id,
        )



    # ---------------------------------------------------------
    # CHECK FOR EXISTING FEEDBACK
    # ---------------------------------------------------------

    existing_feedback = (
        Feedback.objects
        .filter(
            student=request.user,
            course=course,
        )
        .first()
    )


    if existing_feedback:

        return redirect(
            "course_detail",
            course_id=course.id,
        )



    # ---------------------------------------------------------
    # PROCESS FORM
    # ---------------------------------------------------------

    if request.method == "POST":

        form = FeedbackForm(
            request.POST
        )


        if form.is_valid():

            feedback = form.save(
                commit=False
            )


            feedback.student = (
                request.user
            )

            feedback.course = (
                course
            )


            feedback.save()


            return redirect(
                "course_detail",
                course_id=course.id,
            )


    else:

        form = FeedbackForm()



    return render(
        request,
        "courses/create_feedback.html",
        {
            "form": form,
            "course": course,
        },
    )



# =========================================================
# COURSE STUDENTS
# =========================================================

@login_required
def course_students(request, course_id):

    if request.user.role != "teacher":

        return redirect(
            "student_dashboard"
        )


    course = get_object_or_404(
        Course,
        id=course_id,
    )



    # ---------------------------------------------------------
    # ONLY COURSE OWNER CAN MANAGE STUDENTS
    # ---------------------------------------------------------

    if course.teacher != request.user:

        return redirect(
            "teacher_courses"
        )



    enrolments = (
        Enrolment.objects
        .filter(
            course=course
        )
        .select_related(
            "student"
        )
        .order_by(
            "-enrolled_at"
        )
    )



    blocked_students = (
        CourseBlock.objects
        .filter(
            course=course
        )
        .select_related(
            "student"
        )
    )



    return render(
        request,
        "courses/course_students.html",
        {
            "course": course,

            "enrolments":
                enrolments,

            "blocked_students":
                blocked_students,
        },
    )



# =========================================================
# REMOVE STUDENT
# =========================================================

@login_required
def remove_student(
    request,
    course_id,
    student_id,
):

    if request.user.role != "teacher":

        return redirect(
            "student_dashboard"
        )


    if request.method != "POST":

        return redirect(
            "course_students",
            course_id=course_id,
        )


    course = get_object_or_404(
        Course,
        id=course_id,
    )



    # ---------------------------------------------------------
    # CHECK COURSE OWNERSHIP
    # ---------------------------------------------------------

    if course.teacher != request.user:

        return redirect(
            "teacher_courses"
        )



    Enrolment.objects.filter(
        course=course,
        student_id=student_id,
    ).delete()



    return redirect(
        "course_students",
        course_id=course.id,
    )



# =========================================================
# BLOCK STUDENT
# =========================================================

@login_required
def block_student(
    request,
    course_id,
    student_id,
):

    if request.user.role != "teacher":

        return redirect(
            "student_dashboard"
        )


    if request.method != "POST":

        return redirect(
            "course_students",
            course_id=course_id,
        )


    course = get_object_or_404(
        Course,
        id=course_id,
    )



    # ---------------------------------------------------------
    # CHECK COURSE OWNERSHIP
    # ---------------------------------------------------------

    if course.teacher != request.user:

        return redirect(
            "teacher_courses"
        )



    student = get_object_or_404(
        CustomUser,
        id=student_id,
    )



    # ---------------------------------------------------------
    # CREATE BLOCK
    # ---------------------------------------------------------

    CourseBlock.objects.get_or_create(
        student=student,
        course=course,
    )



    # ---------------------------------------------------------
    # REMOVE CURRENT ENROLMENT
    # ---------------------------------------------------------

    Enrolment.objects.filter(
        course=course,
        student=student,
    ).delete()



    return redirect(
        "course_students",
        course_id=course.id,
    )



# =========================================================
# UPLOAD MATERIAL
# =========================================================

@login_required
def upload_material(request, course_id):


    # ---------------------------------------------------------
    # ONLY TEACHERS CAN UPLOAD
    # ---------------------------------------------------------

    if request.user.role != "teacher":

        return redirect(
            "student_dashboard"
        )


    course = get_object_or_404(
        Course,
        id=course_id,
    )



    # ---------------------------------------------------------
    # ONLY COURSE OWNER CAN UPLOAD
    # ---------------------------------------------------------

    if course.teacher != request.user:

        return redirect(
            "teacher_courses"
        )



    # ---------------------------------------------------------
    # PROCESS FORM
    # ---------------------------------------------------------

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



            # -------------------------------------------------
            # NOTIFY ENROLLED STUDENTS USING CELERY
            # -------------------------------------------------

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



# =========================================================
# EDIT COURSE
# =========================================================

@login_required
def edit_course(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id,
    )



    # ---------------------------------------------------------
    # TEACHER ONLY
    # ---------------------------------------------------------

    if request.user.role != "teacher":

        return redirect(
            "student_dashboard"
        )



    # ---------------------------------------------------------
    # COURSE OWNER ONLY
    # ---------------------------------------------------------

    if course.teacher != request.user:

        return redirect(
            "teacher_courses"
        )



    # ---------------------------------------------------------
    # PROCESS FORM
    # ---------------------------------------------------------

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



# =========================================================
# STUDENT COURSES
# =========================================================

@login_required
def student_courses(request):

    if request.user.role != "student":

        return redirect(
            "teacher_dashboard"
        )



    enrolments = (
        Enrolment.objects
        .filter(
            student=request.user
        )
        .select_related(
            "course",
            "course__teacher",
        )
        .order_by(
            "-enrolled_at"
        )
    )



    return render(
        request,
        "courses/student_courses.html",
        {
            "enrolments":
                enrolments,
        },
    )