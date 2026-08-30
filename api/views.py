from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from rest_framework import (
    generics,
    permissions,
    status,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CustomUser

from courses.models import (
    Course,
    CourseMaterial,
    Enrolment,
    Feedback,
)

from notifications.models import Notification

from .permissions import (
    IsTeacher,
    IsTeacherOrSelf,
)

from .serializers import (
    CourseMaterialSerializer,
    CourseSerializer,
    CustomUserSerializer,
    EnrolmentSerializer,
    FeedbackSerializer,
    NotificationSerializer,
)


# ============================================================
# USER API
# ============================================================


@extend_schema(
    summary="List all users",
    description=(
        "Returns a list of all registered users in the "
        "LearnSpace platform. This endpoint is restricted "
        "to authenticated teachers only."
    ),
    responses=CustomUserSerializer(many=True),
)
class UserListAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all().order_by("username")
    serializer_class = CustomUserSerializer
    permission_classes = [IsTeacher]


@extend_schema(
    summary="Retrieve a specific user",
    description=(
        "Returns the profile data of a specific user. "
        "Teachers may view any user, while students may "
        "only view their own account."
    ),
    responses=CustomUserSerializer,
)
class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsTeacherOrSelf,
    ]


class CurrentUserAPIView(generics.GenericAPIView):
    serializer_class = CustomUserSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    @extend_schema(
        summary="Get current user",
        description=(
            "Returns the profile information of the "
            "currently authenticated user."
        ),
        responses=CustomUserSerializer,
    )
    def get(self, request):
        serializer = self.get_serializer(
            request.user,
            context={
                "request": request,
            },
        )

        return Response(serializer.data)

    @extend_schema(
        summary="Update current user",
        description=(
            "Partially updates the profile information of "
            "the currently authenticated user. Read-only "
            "fields such as the user ID, username and role "
            "cannot be changed through this endpoint."
        ),
        request=CustomUserSerializer,
        responses=CustomUserSerializer,
    )
    def patch(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(serializer.data)


# ============================================================
# CURRENT USER ENROLMENTS
# ============================================================


@extend_schema(
    summary="Get my enrolments",
    description=(
        "Returns the courses in which the currently "
        "authenticated user is enrolled."
    ),
    responses=EnrolmentSerializer(many=True),
)
class CurrentUserEnrolmentsAPIView(
    generics.ListAPIView
):
    serializer_class = EnrolmentSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        return (
            Enrolment.objects
            .filter(
                student=self.request.user
            )
            .select_related(
                "course",
                "course__teacher",
            )
            .order_by("-enrolled_at")
        )


# ============================================================
# CURRENT USER NOTIFICATIONS
# ============================================================


@extend_schema(
    summary="Get my notifications",
    description=(
        "Returns notifications belonging only to the "
        "currently authenticated user."
    ),
    responses=NotificationSerializer(many=True),
)
class CurrentUserNotificationsAPIView(
    generics.ListAPIView
):
    serializer_class = NotificationSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        return (
            Notification.objects
            .filter(
                recipient=self.request.user
            )
            .select_related("course")
            .order_by("-created_at")
        )


# ============================================================
# COURSE API
# ============================================================


@extend_schema(
    summary="List courses",
    description=(
        "Returns all courses available on LearnSpace."
    ),
    responses=CourseSerializer(many=True),
)
class CourseListAPIView(
    generics.ListAPIView
):
    queryset = (
        Course.objects
        .select_related("teacher")
        .prefetch_related("enrolments")
        .all()
    )

    serializer_class = CourseSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]


@extend_schema(
    summary="Retrieve a course",
    description=(
        "Returns detailed information for a specific "
        "LearnSpace course."
    ),
    responses=CourseSerializer,
)
class CourseDetailAPIView(
    generics.RetrieveAPIView
):
    queryset = (
        Course.objects
        .select_related("teacher")
        .prefetch_related("enrolments")
        .all()
    )

    serializer_class = CourseSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]


# ============================================================
# COURSE MATERIAL API
# ============================================================


class CourseMaterialsAPIView(
    generics.ListAPIView
):
    serializer_class = CourseMaterialSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    @extend_schema(
        summary="List course materials",
        description=(
            "Returns teaching materials for a course. "
            "Only the teacher who owns the course or a "
            "student enrolled in the course may access "
            "the materials."
        ),
        responses=CourseMaterialSerializer(
            many=True
        ),
    )
    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        course = get_object_or_404(
            Course,
            pk=self.kwargs["pk"],
        )

        is_teacher = (
            course.teacher_id
            == request.user.id
        )

        is_enrolled = (
            Enrolment.objects.filter(
                course=course,
                student=request.user,
            ).exists()
        )

        if (
            not is_teacher
            and not is_enrolled
        ):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to access these materials."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().get(
            request,
            *args,
            **kwargs,
        )

    def get_queryset(self):
        return (
            CourseMaterial.objects
            .filter(
                course_id=self.kwargs["pk"]
            )
            .select_related("course")
            .order_by("-uploaded_at")
        )


# ============================================================
# COURSE STUDENT API
# ============================================================


class CourseStudentsAPIView(
    generics.ListAPIView
):
    serializer_class = CustomUserSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    @extend_schema(
        summary="List enrolled students",
        description=(
            "Returns students enrolled in the selected "
            "course. Only the teacher who owns the course "
            "may access this endpoint."
        ),
        responses=CustomUserSerializer(
            many=True
        ),
    )
    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        course = get_object_or_404(
            Course,
            pk=self.kwargs["pk"],
        )

        if (
            course.teacher
            != request.user
        ):
            return Response(
                {
                    "detail": (
                        "Only the course teacher "
                        "can view enrolled students."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().get(
            request,
            *args,
            **kwargs,
        )

    def get_queryset(self):
        return (
            CustomUser.objects
            .filter(
                enrolments__course_id=(
                    self.kwargs["pk"]
                ),
                role=CustomUser.STUDENT,
            )
            .distinct()
            .order_by("username")
        )


# ============================================================
# COURSE ENROLMENT API
# ============================================================


class CourseEnrolAPIView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    @extend_schema(
        summary="Enrol in a course",
        description=(
            "Allows an authenticated student to enrol "
            "in a course. Teachers cannot enrol as "
            "students and duplicate enrolments are "
            "prevented."
        ),
        request=None,
        responses={
            201: EnrolmentSerializer,
        },
    )
    def post(
        self,
        request,
        pk,
    ):
        if (
            request.user.role
            != CustomUser.STUDENT
        ):
            return Response(
                {
                    "detail": (
                        "Only students can enrol "
                        "in courses."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        course = get_object_or_404(
            Course,
            pk=pk,
        )

        enrolment, created = (
            Enrolment.objects.get_or_create(
                student=request.user,
                course=course,
            )
        )

        if not created:
            return Response(
                {
                    "detail": (
                        "You are already enrolled "
                        "in this course."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EnrolmentSerializer(
            enrolment,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# COURSE FEEDBACK API
# ============================================================


class CourseFeedbackAPIView(
    generics.ListCreateAPIView
):
    serializer_class = FeedbackSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        return (
            Feedback.objects
            .filter(
                course_id=self.kwargs["pk"]
            )
            .select_related(
                "student",
                "course",
            )
            .order_by("-created_at")
        )

    @extend_schema(
        summary="List course feedback",
        description=(
            "Returns feedback submitted for the "
            "selected course."
        ),
        responses=FeedbackSerializer(
            many=True
        ),
    )
    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        return super().get(
            request,
            *args,
            **kwargs,
        )

    @extend_schema(
        summary="Submit course feedback",
        description=(
            "Allows an enrolled student to submit "
            "one feedback record for the selected "
            "course. The student must already be "
            "enrolled in the course."
        ),
        request=FeedbackSerializer,
        responses={
            201: FeedbackSerializer,
        },
    )
    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        course = get_object_or_404(
            Course,
            pk=self.kwargs["pk"],
        )

        if (
            request.user.role
            != CustomUser.STUDENT
        ):
            return Response(
                {
                    "detail": (
                        "Only students may "
                        "submit feedback."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        is_enrolled = (
            Enrolment.objects.filter(
                course=course,
                student=request.user,
            ).exists()
        )

        if not is_enrolled:
            return Response(
                {
                    "detail": (
                        "You must be enrolled "
                        "before submitting feedback."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        feedback_exists = (
            Feedback.objects.filter(
                course=course,
                student=request.user,
            ).exists()
        )

        if feedback_exists:
            return Response(
                {
                    "detail": (
                        "You have already submitted "
                        "feedback for this course."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().post(
            request,
            *args,
            **kwargs,
        )

    def perform_create(
        self,
        serializer,
    ):
        course = get_object_or_404(
            Course,
            pk=self.kwargs["pk"],
        )

        serializer.save(
            student=self.request.user,
            course=course,
        )


# ============================================================
# NOTIFICATION API
# ============================================================


class NotificationReadAPIView(
    generics.UpdateAPIView
):
    serializer_class = NotificationSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    http_method_names = [
        "patch",
    ]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        )

    @extend_schema(
        summary="Mark notification as read",
        description=(
            "Marks a notification belonging to the "
            "currently authenticated user as read. "
            "Users cannot modify another user's "
            "notifications."
        ),
        request=None,
        responses=NotificationSerializer,
    )
    def patch(
        self,
        request,
        *args,
        **kwargs,
    ):
        notification = self.get_object()

        notification.is_read = True

        notification.save(
            update_fields=[
                "is_read",
            ]
        )

        serializer = self.get_serializer(
            notification
        )

        return Response(serializer.data)