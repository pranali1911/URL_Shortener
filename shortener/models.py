from django.db import models

from django.contrib.auth.models import User

class URL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    original_url = models.URLField()
    short_code = models.CharField(max_length=50, unique=True, blank=True)
    custom_alias = models.CharField(max_length=50, unique=True, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.short_code

class ClickEvent(models.Model):
    url = models.ForeignKey(URL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    referrer = models.CharField(max_length=500, blank=True)
    device = models.CharField(max_length=100, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    ip_address = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.url.short_code
    
class Analytics(models.Model):
    url = models.ForeignKey(URL, on_delete=models.CASCADE)
    date = models.DateField()
    clicks = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    aggregated_metrics = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.url.short_code} - {self.date}"