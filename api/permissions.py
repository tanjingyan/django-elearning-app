from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    """
    Allow access only to authenticated teachers.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "teacher"
        )


class IsTeacherOrSelf(BasePermission):
    """
    Teachers can access any user.
    Students can access only their own user record.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.role == "teacher":
            return True

        return obj.id == request.user.id