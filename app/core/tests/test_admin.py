"""
Tests for the Django admin modifications.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Create user and client."""

        self.client = Client()
        self.superuser = get_user_model().objects.create_superuser(
            username="admin",
            password="test1234",
        )
        self.client.force_login(self.superuser)
        self.user = get_user_model().objects.create(
            username="user",
            password="test1234",
        )

    def test_users_list(self):
        """Test that users are listed on page."""

        url = reverse("admin:core_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.username)

    def test_edit_user_page(self):
        """Test the edit user page works."""

        url = reverse("admin:core_user_change", args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_page(self):
        """Test the create user page works."""

        url = reverse("admin:core_user_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
