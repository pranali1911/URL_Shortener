from django.contrib import admin
from .models import URL, ClickEvent, Analytics


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "original_url",
        "short_code",
        "custom_alias",
        "status",
        "expires_at",
        "created_at"
    )
    list_filter = ("status",)
    search_fields = ("original_url", "short_code", "custom_alias")


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "url",
        "timestamp",
        "referrer",
        "device",
        "browser",
        "country"
    )
    list_filter = ("device", "browser")
    search_fields = ("url__short_code", "referrer")


@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ("id", "url", "date", "clicks", "unique_visitors")
    list_filter = ("date",)
    search_fields = ("url__short_code",)