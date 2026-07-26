from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser
from .forms import CustomUserCreationForm, StatusUpdateForm


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

    return render(
        request,
        "accounts/student_dashboard.html"
    )


@login_required
def teacher_dashboard(request):

    return render(
        request,
        "accounts/teacher_dashboard.html"
    )

def profile(request, username):

    from .models import CustomUser

    user_profile = get_object_or_404(
        CustomUser,
        username=username
    )

    statuses = user_profile.status_updates.all()

    return render(
        request,
        "accounts/profile.html",
        {
            "user_profile": user_profile,
            "statuses": statuses,
        }
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