from celery import shared_task

from accounts.models import CustomUser
from courses.models import (
    Course,
    CourseMaterial,
    Enrolment,
)

from .models import Notification


@shared_task
def create_enrolment_notification(
    enrolment_id,
):
    try:
        enrolment = (
            Enrolment.objects.select_related(
                "student",
                "course__teacher",
            ).get(
                id=enrolment_id
            )
        )

    except Enrolment.DoesNotExist:
        return

    Notification.objects.create(
        recipient=enrolment.course.teacher,
        course=enrolment.course,
        notification_type=Notification.ENROLMENT,
        message=(
            f"{enrolment.student.username} "
            f'enrolled in "{enrolment.course.title}".'
        ),
    )


@shared_task
def create_material_notifications(
    material_id,
):
    try:
        material = (
            CourseMaterial.objects.select_related(
                "course"
            ).get(
                id=material_id
            )
        )

    except CourseMaterial.DoesNotExist:
        return

    enrolments = (
        Enrolment.objects.filter(
            course=material.course
        ).select_related(
            "student"
        )
    )

    notifications = []

    for enrolment in enrolments:
        notifications.append(
            Notification(
                recipient=enrolment.student,
                course=material.course,
                notification_type=Notification.MATERIAL,
                message=(
                    f'New material "{material.title}" '
                    f"has been added to "
                    f'"{material.course.title}".'
                ),
            )
        )

    Notification.objects.bulk_create(
        notifications
    )

@shared_task
def create_block_notification(student_id, course_id):

    student = CustomUser.objects.get(
        id=student_id
    )

    course = Course.objects.get(
        id=course_id
    )

    Notification.objects.create(
        recipient=student,
        course=course,
        notification_type="block",
        message=(
            f"You have been blocked from "
            f"{course.title}. You can no longer "
            f"access or enrol in this course."
        ),
    )

@shared_task
def create_unblock_notification(student_id, course_id):

    student = CustomUser.objects.get(
        id=student_id
    )

    course = Course.objects.get(
        id=course_id
    )

    Notification.objects.create(
        recipient=student,
        course=course,
        notification_type="unblock",
        message=(
            f"You have been unblocked from "
            f"{course.title}. You can now enrol "
            f"in this course again."
        ),
    )

@shared_task
def create_removal_notification(student_id, course_id):

    student = CustomUser.objects.get(
        id=student_id
    )

    course = Course.objects.get(
        id=course_id
    )

    Notification.objects.create(
        recipient=student,
        course=course,
        notification_type="remove",
        message=(
            f"You have been removed from "
            f"{course.title}. You are no longer "
            f"enrolled in this course, but you "
            f"can enrol again."
        ),
    )