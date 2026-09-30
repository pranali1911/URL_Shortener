from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from django.shortcuts import redirect
from django.utils import timezone
from django.db.models import Count
from django.core.cache import cache
from django.shortcuts import redirect, render

from user_agents import parse

from .serializers import URLSerializer
from .tasks import update_analytics
from .models import URL, ClickEvent, Analytics

import hashlib
import logging
import time

logger = logging.getLogger("shortener")

class URLCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
       urls = URL.objects.filter(user=request.user).order_by("-created_at")
       paginator = PageNumberPagination()
       paginator.page_size = 10
        
       page = paginator.paginate_queryset(urls, request)
       serializer = URLSerializer(page, many=True)

       return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = URLSerializer(data=request.data)

        if serializer.is_valid():
            url = serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class URLDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            url = URL.objects.get(id=id)
        except URL.DoesNotExist:
            return Response(
                {"detail": "URL not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if url.user != request.user:
            return Response(
                {"detail": "You do not have permission to access this URL."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = URLSerializer(url)
        return Response(serializer.data)

    def put(self, request, id):
        try:
            url = URL.objects.get(id=id)
        except URL.DoesNotExist:
            return Response(
                {"detail": "URL not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if url.user != request.user:
            return Response(
                {"detail": "You do not have permission to edit this URL."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = URLSerializer(url, data=request.data)

        if serializer.is_valid():
            serializer.save()

            cache_key = f"url:{url.short_code}"
            cache.delete(cache_key)

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, id):
        try:
            url = URL.objects.get(id=id)
        except URL.DoesNotExist:
            return Response(
                {"detail": "URL not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if url.user != request.user:
            return Response(
                {"detail": "You do not have permission to delete this URL."},
                status=status.HTTP_403_FORBIDDEN
            )

        cache_key = f"url:{url.short_code}"
        cache.delete(cache_key)

        url.delete()

        return Response(
            {"detail": "URL deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
        
class URLAnalyticsView(APIView):
    def get(self, request, id):
        try:
            url = URL.objects.get(id=id)
        except URL.DoesNotExist:
            return Response(
                {"detail": "URL not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        total_clicks = ClickEvent.objects.filter(url=url).count()
        update_analytics.delay(url.id)

        clicks_over_time = (
            ClickEvent.objects
            .filter(url=url)
            .values("timestamp__date")
            .annotate(clicks=Count("id"))
            .order_by("timestamp__date")
        )

        referrers = (
            ClickEvent.objects
            .filter(url=url)
            .values("referrer")
            .annotate(clicks=Count("id"))
            .order_by("-clicks")
        )

        unique_visitors = (
            ClickEvent.objects
            .filter(url=url)
            .values("ip_address")
            .distinct()
            .count()
        )

        devices = (
            ClickEvent.objects
            .filter(url=url)
            .values("device")
            .annotate(clicks=Count("id"))
            .order_by("-clicks")
        )

        browsers = (
            ClickEvent.objects
            .filter(url=url)
            .values("browser")
            .annotate(clicks=Count("id"))
            .order_by("-clicks")
        )
        
        

   
        return Response({
            "url_id": url.id,
            "short_code": url.short_code,
            "total_clicks": total_clicks,
            "clicks_over_time": clicks_over_time,
            "referrers": referrers,
            "unique_visitors": unique_visitors,
            "devices": devices,
            "browsers": browsers
        })
        
class URLRedirectView(APIView):
    def get(self, request, short_code):

        start_time = time.time()

        cache_key = f"url:{short_code}"

        url_id = cache.get(cache_key)

        if url_id:
            try:
                url = URL.objects.get(id=url_id)
            except URL.DoesNotExist:
                cache.delete(cache_key)
                return Response(
                    {"detail": "URL not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            try:
                url = URL.objects.get(short_code=short_code)
            except URL.DoesNotExist:
                return Response(
                    {"detail": "URL not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            cache.set(cache_key, url.id, timeout=3600)

        if not url.status:
            return Response(
                {"detail": "This URL is inactive."},
                status=status.HTTP_404_NOT_FOUND
            )

        if url.expires_at and url.expires_at <= timezone.now():
            return Response(
                {"detail": "This URL has expired."},
                status=status.HTTP_410_GONE
            )

        user_agent = parse(request.META.get("HTTP_USER_AGENT", ""))

        ClickEvent.objects.create(
            url=url,
            referrer=request.META.get("HTTP_REFERER", ""),
            device=user_agent.device.family,
            browser=user_agent.browser.family,
            ip_address=hashlib.sha256(
                request.META.get("REMOTE_ADDR", "").encode()
            ).hexdigest()
        )

        response_time = time.time() - start_time

        logger.info(
            "Redirect short_code=%s response_time=%.4f seconds",
            short_code,
            response_time
        )

        return redirect(url.original_url)
    
    

def home(request):
    return render(request, "shortener/index.html")