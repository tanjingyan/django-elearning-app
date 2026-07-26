from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Notification


@login_required
def notification_list(request):

    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "notifications/notification_list.html",
        {
            "notifications": notifications,
        }
    )


@login_required
def mark_notification_read(
    request,
    notification_id
):

    notification = Notification.objects.get(
        id=notification_id,
        recipient=request.user
    )

    notification.is_read = True

    notification.save()

    if notification.course:

        return redirect(
            "course_detail",
            course_id=notification.course.id
        )

    return redirect(
        "notification_list"
    )