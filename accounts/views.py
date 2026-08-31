from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser, StatusUpdate
from .forms import CustomUserCreationForm, StatusUpdateForm, EditProfileForm
from courses.models import Course, Enrolment

def home_redirect(request):
    if request.user.is_authenticated:
        if request.user.role == "teacher":
            return redirect("teacher_dashboard")

        return redirect("student_dashboard")

    return redirect("login")

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()

            # Log the new user in automatically
            login(request, user)

            # Redirect based on role
            if user.role == "teacher":
                return redirect("teacher_dashboard")
            else:
                return redirect("student_dashboard")

    else:
        form = CustomUserCreationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )


def login_view(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Redirect based on role
            if user.role == "teacher":
                return redirect("teacher_dashboard")
            else:
                return redirect("student_dashboard")

        else:

            return render(
                request,
                "accounts/login.html",
                {
                    "error": "Invalid username or password."
                }
            )

    return render(
        request,
        "accounts/login.html"
    )


def logout_view(request):
    logout(request)

    return redirect("login")


@login_required
def student_dashboard(request):

    if request.user.role != "student":
        return redirect("teacher_dashboard")

    enrolments = (
        Enrolment.objects.filter(
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

    featured_enrolment = enrolments.first()

    return render(
        request,
        "accounts/student_dashboard.html",
        {
            "enrolments": enrolments,
            "featured_enrolment": featured_enrolment,
            "enrolled_course_count": enrolments.count(),
        },
    )

@login_required
def teacher_dashboard(request):

    return render(
        request,
        "accounts/teacher_dashboard.html"
    )

@login_required
def profile(request, username):

    profile_user = get_object_or_404(
        CustomUser,
        username=username,
    )

    # Status updates belonging to this user
    status_updates = StatusUpdate.objects.filter(
        user=profile_user,
    ).order_by(
        "-created_at"
    )

    courses_created = []
    enrolments = []

    # Teacher home page:
    # show courses created by the teacher
    if profile_user.role == "teacher":

        courses_created = (
            Course.objects.filter(
                teacher=profile_user
            )
            .order_by(
                "-created_at"
            )
        )

    # Student home page:
    # show courses the student is enrolled in
    elif profile_user.role == "student":

        enrolments = (
            Enrolment.objects.filter(
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
            "profile_user": profile_user,
            "status_updates": status_updates,

            "courses_created": courses_created,
            "enrolments": enrolments,

            "courses_created_count": len(
                courses_created
            ),

            "courses_enrolled_count": len(
                enrolments
            ),

            "status_count": status_updates.count(),
        },
    )

@login_required
def create_status(request):

    if request.method == "POST":

        form = StatusUpdateForm(request.POST)

        if form.is_valid():

            status = form.save(
                commit=False
            )

            status.user = request.user

            status.save()

            return redirect(
                "profile",
                username=request.user.username
            )

    else:

        form = StatusUpdateForm()

    return render(
        request,
        "accounts/create_status.html",
        {
            "form": form
        }
    )

@login_required
def search_users(request):

    # Only teachers can access this page
    if request.user.role != "teacher":
        return redirect("student_dashboard")

    query = request.GET.get("q", "")

    users = []

    if query:
        users = CustomUser.objects.filter(
            username__icontains=query
        ).exclude(
            id=request.user.id
        )

    return render(
        request,
        "accounts/search_users.html",
        {
            "users": users,
            "query": query,
        }
    )

@login_required
def teacher_dashboard(request):

    if request.user.role != "teacher":
        return redirect("student_dashboard")

    return render(
        request,
        "accounts/teacher_dashboard.html"
    )

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Your profile has been updated successfully.",
            )

            return redirect(
                "profile",
                username=request.user.username,
            )

    else:
        form = EditProfileForm(
            instance=request.user,
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form": form,
        },
    )

@login_required
def api_docs(request):
    if request.user.role != "teacher":
        messages.error(
            request,
            "API documentation is available to teachers only.",
        )

        return redirect(
            "student_dashboard"
        )

    return render(
        request,
        "api_docs.html",
    )