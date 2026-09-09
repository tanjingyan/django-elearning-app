from datetime import timedelta

from django import template
from django.utils import timezone
from django.utils.timesince import timesince


register = template.Library()


@register.filter
def status_datetime(value):

    if not value:
        return ""

    now = timezone.now()

    difference = now - value

    # Less than 24 hours:
    # display relative time
    if difference < timedelta(hours=24):

        return f"{timesince(value, now)} ago"

    # After 24 hours:
    # display DD/MM/YYYY
    local_value = timezone.localtime(value)

    return local_value.strftime("%d/%m/%Y")