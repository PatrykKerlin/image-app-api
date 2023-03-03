"""
Tests for the Django admin modifications.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status

from core.models import Tier, ThumbnailSize


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
        self.tier = Tier.objects.create(name="test")
        self.thumb = ThumbnailSize.objects.create(tier=self.tier, height=200)
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234",
            tier=self.tier,
        )

    # Users page
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

    # Tiers page
    def test_tiers_list(self):
        """Test that tiers are listed on page."""

        url = reverse("admin:core_tier_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.tier.name)

    def test_edit_tier_page(self):
        """Test the edit tier page works."""

        url = reverse("admin:core_tier_change", args=[self.tier.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_tier_page(self):
        """Test the create tier page works."""

        url = reverse("admin:core_tier_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Thumbnail sizes page
    def test_thumbnail_sizes_list(self):
        """Test that thumbnail sizes are listed on page."""

        url = reverse("admin:core_thumbnailsize_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.thumb.height)

    def test_edit_thumbnail_sizes_page(self):
        """Test the edit thumbnail sizes page works."""

        url = reverse("admin:core_thumbnailsize_change", args=[self.thumb.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_thumbnail_size_page(self):
        """Test the create thumbnail size page works."""

        url = reverse("admin:core_thumbnailsize_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
