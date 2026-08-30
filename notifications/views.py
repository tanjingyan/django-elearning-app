from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
    redirect,
)
from django.views.decorators.http import require_POST

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
        },
    )


@login_required
@require_POST
def mark_notification_read(
    request,
    notification_id,
):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user,
    )

    notification.is_read = True
    notification.save(
        update_fields=["is_read"]
    )

    # HTMX request:
    # return only the updated notification
    if request.headers.get("HX-Request") == "true":

        return render(
            request,
            "notifications/partials/notification_item.html",
            {
                "notification": notification,
            },
        )

    # Normal request fallback
    if notification.course:

        return redirect(
            "course_detail",
            course_id=notification.course.id,
        )

    return redirect(
        "notification_list"
    )