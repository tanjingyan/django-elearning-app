from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from .models import CustomUser, StatusUpdate
from .forms import (
    CustomUserCreationForm,
    StatusUpdateForm,
    EditProfileForm,
)

from courses.models import Course, Enrolment


# =========================================================
# HOME REDIRECT
# =========================================================

def home_redirect(request):

    if request.user.is_authenticated:

        if request.user.role == "teacher":
            return redirect(
                "teacher_dashboard"
            )

        return redirect(
            "student_dashboard"
        )

    return redirect(
        "login"
    )


# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.user.is_authenticated:

        if request.user.role == "teacher":
            return redirect(
                "teacher_dashboard"
            )

        return redirect(
            "student_dashboard"
        )


    if request.method == "POST":

        form = CustomUserCreationForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            form.save()

            return redirect(
                "login"
            )

    else:

        form = CustomUserCreationForm()


    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(
                request,
                user,
            )

            # Redirect based on role
            if user.role == "teacher":

                return redirect(
                    "teacher_dashboard"
                )

            else:

                return redirect(
                    "student_dashboard"
                )

        else:

            return render(
                request,
                "accounts/login.html",
                {
                    "error":
                        "Invalid username or password."
                },
            )


    return render(
        request,
        "accounts/login.html",
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(
        request
    )

    return redirect(
        "login"
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@login_required
def student_dashboard(request):

    # =====================================================
    # ROLE CHECK
    # =====================================================

    if request.user.role != "student":

        return redirect(
            "teacher_dashboard"
        )


    # =====================================================
    # STUDENT ENROLMENTS
    # =====================================================

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


    # =====================================================
    # ENROLLED COURSE COUNT
    # =====================================================

    enrolled_course_count = (
        enrolments.count()
    )


    # =====================================================
    # CONTINUE LEARNING
    #
    # First try to display the last enrolled course
    # that the student actually opened.
    # =====================================================

    featured_enrolment = None


    last_viewed_course_id = (
        request.session.get(
            "last_viewed_course_id"
        )
    )


    # -----------------------------------------------------
    # LAST VIEWED COURSE
    # -----------------------------------------------------

    if last_viewed_course_id:

        featured_enrolment = (
            enrolments
            .filter(
                course_id=
                    last_viewed_course_id
            )
            .first()
        )


    # -----------------------------------------------------
    # FALLBACK
    #
    # If the student has never opened an enrolled course,
    # show their most recently enrolled course instead.
    # -----------------------------------------------------

    if featured_enrolment is None:

        featured_enrolment = (
            enrolments.first()
        )


    # =====================================================
    # RENDER DASHBOARD
    # =====================================================

    return render(
        request,
        "accounts/student_dashboard.html",
        {
            "enrolments":
                enrolments,

            "enrolled_course_count":
                enrolled_course_count,

            "featured_enrolment":
                featured_enrolment,
        },
    )


# =========================================================
# TEACHER DASHBOARD
# =========================================================

@login_required
def teacher_dashboard(request):

    # Only teachers may access this dashboard
    if request.user.role != "teacher":

        return redirect(
            "student_dashboard"
        )


    # -----------------------------------------------------
    # COURSES CREATED BY THIS TEACHER
    # -----------------------------------------------------

    courses = (
        Course.objects
        .filter(
            teacher=request.user
        )
        .order_by(
            "-created_at"
        )
    )

    course_count = (
        courses.count()
    )


    # -----------------------------------------------------
    # ENROLMENTS ACROSS THE TEACHER'S COURSES
    # -----------------------------------------------------

    teacher_enrolments = (
        Enrolment.objects
        .filter(
            course__teacher=
                request.user
        )
        .select_related(
            "student",
            "course",
        )
    )


    # Total enrolment records
    total_enrolments = (
        teacher_enrolments.count()
    )


    # Unique students
    #
    # Example:
    # Student A enrolled in Course 1 + Course 2
    # = 1 unique student
    # = 2 total enrolments

    total_students = (
        teacher_enrolments
        .values(
            "student_id"
        )
        .distinct()
        .count()
    )


    # -----------------------------------------------------
    # RECENT DATA
    # -----------------------------------------------------

    recent_courses = (
        courses[:3]
    )

    recent_enrolments = (
        teacher_enrolments
        .order_by(
            "-enrolled_at"
        )[:5]
    )


    # -----------------------------------------------------
    # TEMPLATE
    # -----------------------------------------------------

    return render(
        request,
        "accounts/teacher_dashboard.html",
        {
            "course_count":
                course_count,

            "total_students":
                total_students,

            "total_enrolments":
                total_enrolments,

            "recent_courses":
                recent_courses,

            "recent_enrolments":
                recent_enrolments,
        },
    )


# =========================================================
# PROFILE
# =========================================================

@login_required
def profile(request, username):

    profile_user = get_object_or_404(
        CustomUser,
        username=username,
    )


    # Status updates belonging to this user
    status_updates = (
        StatusUpdate.objects
        .filter(
            user=profile_user
        )
        .order_by(
            "-created_at"
        )
    )


    courses_created = []
    enrolments = []


    # -----------------------------------------------------
    # TEACHER PROFILE
    # -----------------------------------------------------

    if profile_user.role == "teacher":

        courses_created = (
            Course.objects
            .filter(
                teacher=profile_user
            )
            .order_by(
                "-created_at"
            )
        )


    # -----------------------------------------------------
    # STUDENT PROFILE
    # -----------------------------------------------------

    elif profile_user.role == "student":

        enrolments = (
            Enrolment.objects
            .filter(
                student=profile_user
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
        "accounts/profile.html",
        {
            "profile_user":
                profile_user,

            "status_updates":
                status_updates,

            "courses_created":
                courses_created,

            "enrolments":
                enrolments,

            "courses_created_count":
                len(
                    courses_created
                ),

            "courses_enrolled_count":
                len(
                    enrolments
                ),

            "status_count":
                status_updates.count(),
        },
    )


# =========================================================
# CREATE STATUS UPDATE
# =========================================================

@login_required
def create_status(request):

    if request.method == "POST":

        form = StatusUpdateForm(
            request.POST
        )

        if form.is_valid():

            status = form.save(
                commit=False
            )

            status.user = (
                request.user
            )

            status.save()

            return redirect(
                "profile",
                username=
                    request.user.username,
            )

    else:

        form = StatusUpdateForm()


    return render(
        request,
        "accounts/create_status.html",
        {
            "form":
                form
        },
    )


# =========================================================
# SEARCH USERS
# =========================================================

@login_required
def search_users(request):

    # Only teachers can access this page
    if request.user.role != "teacher":

        return redirect(
            "student_dashboard"
        )


    query = request.GET.get(
        "q",
        "",
    )

    users = []


    if query:

        users = (
            CustomUser.objects
            .filter(
                username__icontains=
                    query
            )
            .exclude(
                id=request.user.id
            )
        )


    return render(
        request,
        "accounts/search_users.html",
        {
            "users":
                users,

            "query":
                query,
        },
    )


# =========================================================
# EDIT PROFILE + CHANGE PASSWORD
# =========================================================

@login_required
def edit_profile(request):

    # -----------------------------------------------------
    # DEFAULT FORMS
    # -----------------------------------------------------

    form = EditProfileForm(
        instance=request.user,
    )

    password_form = PasswordChangeForm(
        user=request.user,
    )


    # Add Bootstrap styling to Django's
    # built-in password fields
    for field in password_form.fields.values():

        field.widget.attrs.update({
            "class":
                "form-control"
        })


    # -----------------------------------------------------
    # POST REQUEST
    # -----------------------------------------------------

    if request.method == "POST":

        # The hidden field in the template tells
        # Django which form was submitted.
        #
        # Default to "profile" for compatibility
        # with the original Edit Profile form.

        form_type = request.POST.get(
            "form_type",
            "profile",
        )


        # =================================================
        # EDIT PROFILE FORM
        # =================================================

        if form_type == "profile":

            form = EditProfileForm(
                request.POST,
                request.FILES,
                instance=request.user,
            )


            if form.is_valid():

                form.save()


                messages.success(
                    request,
                    (
                        "Your profile has been "
                        "updated successfully."
                    ),
                )


                return redirect(
                    "profile",
                    username=
                        request.user.username,
                )


        # =================================================
        # CHANGE PASSWORD FORM
        # =================================================

        elif form_type == "password":

            password_form = (
                PasswordChangeForm(
                    user=request.user,
                    data=request.POST,
                )
            )


            # Apply Bootstrap styling again because
            # this is now a newly created bound form.

            for field in (
                password_form.fields.values()
            ):

                field.widget.attrs.update({
                    "class":
                        "form-control"
                })


            if password_form.is_valid():

                user = (
                    password_form.save()
                )


                # Password changes normally invalidate
                # the current session.
                #
                # This updates the session authentication
                # hash so the user stays logged in.

                update_session_auth_hash(
                    request,
                    user,
                )


                messages.success(
                    request,
                    (
                        "Your password has been "
                        "changed successfully."
                    ),
                )


                return redirect(
                    "profile",
                    username=
                        request.user.username,
                )


    # -----------------------------------------------------
    # TEMPLATE
    # -----------------------------------------------------

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form":
                form,

            "password_form":
                password_form,
        },
    )


# =========================================================
# API DOCUMENTATION
# =========================================================

@login_required
def api_docs(request):

    if request.user.role != "teacher":

        messages.error(
            request,
            (
                "API documentation is "
                "available to teachers only."
            ),
        )


        return redirect(
            "student_dashboard"
        )


    return render(
        request,
        "api_docs.html",
    )