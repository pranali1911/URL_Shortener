from django.test import TestCase, SimpleTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from .models import URL, ClickEvent
from .utils import base62_encode


class Base62Test(SimpleTestCase):

    def test_zero(self):
        self.assertEqual(base62_encode(0), "0")

    def test_one(self):
        self.assertEqual(base62_encode(1), "1")

    def test_sixty_one(self):
        self.assertEqual(base62_encode(61), "Z")

    def test_sixty_two(self):
        self.assertEqual(base62_encode(62), "10")


class URLAPITest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_url(self):
        response = self.client.post(
            "/api/urls",
            {
                "original_url": "https://www.google.com"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(URL.objects.count(), 1)

    def test_list_urls(self):
        URL.objects.create(
            user=self.user,
            original_url="https://www.google.com",
            short_code="test1"
        )

        response = self.client.get("/api/urls")

        self.assertEqual(response.status_code, 200)


class RedirectTest(TestCase):

    def setUp(self):
        self.url = URL.objects.create(
            original_url="https://www.google.com",
            short_code="test123"
        )

    def test_redirect(self):
        response = self.client.get("/test123")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://www.google.com")

    def test_invalid_short_code(self):
        response = self.client.get("/doesnotexist")

        self.assertEqual(response.status_code, 404)

    def test_click_created(self):
        self.client.get("/test123")

        self.assertEqual(
            ClickEvent.objects.filter(url=self.url).count(),
            1
        )