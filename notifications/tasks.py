from celery import shared_task

from courses.models import (
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