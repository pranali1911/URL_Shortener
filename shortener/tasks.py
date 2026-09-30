from celery import shared_task
from django.db.models import Count

from .models import URL, ClickEvent, Analytics


@shared_task
def update_analytics(url_id):
    try:
        url = URL.objects.get(id=url_id)
    except URL.DoesNotExist:
        return

    clicks_over_time = (
        ClickEvent.objects
        .filter(url=url)
        .values("timestamp__date")
        .annotate(clicks=Count("id"))
        .order_by("timestamp__date")
    )

    for data in clicks_over_time:
        date = data["timestamp__date"]

        unique_visitors = (
            ClickEvent.objects
            .filter(
                url=url,
                timestamp__date=date
            )
            .values("ip_address")
            .distinct()
            .count()
        )

        Analytics.objects.update_or_create(
            url=url,
            date=date,
            defaults={
                "clicks": data["clicks"],
                "unique_visitors": unique_visitors,
            }
        )