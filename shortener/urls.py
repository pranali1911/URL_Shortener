from django.urls import path

from .views import (
    URLCreateView,
    URLDetailView,
    URLRedirectView,
    URLAnalyticsView,
    home
)


urlpatterns = [
    path("", home, name="home"),
    path("urls", URLCreateView.as_view()),
    path("urls/<int:id>", URLDetailView.as_view()),
    path("urls/<int:id>/analytics", URLAnalyticsView.as_view()),
    path("<str:short_code>", URLRedirectView.as_view()),
]