"""
Tests for models.
"""

from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core import models


class ModelTests(TestCase):
    """Test models."""

    # Tests for tier model
    def test_create_tier_with_name_successfull(self):
        """Test creating a tier with a name is successful."""

        name = "test"
        tier = models.Tier.objects.create(name=name)

        self.assertEqual(tier.name, name)

    def test_create_tier_without_name_raises_error(self):
        """Test creating a tier without a name raises a ValidationError."""

        with self.assertRaises(ValidationError):
            models.Tier.objects.create(name="")

    # Tests for user model
    def test_create_user_with_username_successful(self):
        """Test creating a user with a username is successful."""

        username = "example_username"
        password = "test1234"
        user = get_user_model().objects.create_user(
            username=username,
            password=password,
            tier=models.Tier.objects.create(name="test"),
        )

        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password, password)

    def test_new_user_without_username_raises_error(self):
        """Test creating a user without a username raises a ValidationError."""

        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                username="",
                password="test1234",
                tier=models.Tier.objects.create(name="test"),
            )

    def test_create_superuser(self):
        """Test creating a superuser."""

        user = get_user_model().objects.create_superuser(
            username="example_username",
            password="test1234",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    # Tests for thumbnail size model
    def test_create_thumbnail_size_successfull(self):
        """Test creating a thumbnail size is successful."""

        height = 200
        tier = models.Tier.objects.create(name="test")
        thumb = models.ThumbnailSize.objects.create(tier=tier, height=height)

        self.assertEqual(thumb.tier, tier)
        self.assertEqual(thumb.height, height)

    def test_create_two_thumbnail_sizes_for_one_tier(self):
        """Test creating 2 thumbnail sizes for 1 tier."""

        height_1 = 200
        height_2 = 300
        tier = models.Tier.objects.create(name="test")
        thumb_1 = models.ThumbnailSize.objects.create(tier=tier, height=height_1)
        thumb_2 = models.ThumbnailSize.objects.create(tier=tier, height=height_2)

        self.assertEqual(thumb_1.tier, tier)
        self.assertEqual(thumb_2.tier, tier)
        self.assertEqual(thumb_1.height, height_1)
        self.assertEqual(thumb_2.height, height_2)

    def test_create_two_identical_thumbnail_sizes_for_one_tier_raises_error(self):
        """Test creating 2 identical thumbnail sizes for 1 tier raises error."""

        with self.assertRaises(ValidationError):
            height = 200
            tier = models.Tier.objects.create(name="test")
            models.ThumbnailSize.objects.create(tier=tier, height=height)
            models.ThumbnailSize.objects.create(tier=tier, height=height)

        self.assertEqual(models.ThumbnailSize.objects.count(), 1)

    def test_create_thumbnail_with_0_height_raises_error(self):
        """Test creating a thumbnail size with 0 height raises ValidationError."""

        with self.assertRaises(ValidationError):
            models.ThumbnailSize.objects.create(
                tier=models.Tier.objects.create(name="test"),
                height=0,
            )

        self.assertEqual(models.ThumbnailSize.objects.count(), 0)

    def test_create_thumbnail_for_no_thumb_tier_raises_error(self):
        """Test creating a thumbnail size with 0 height raises ValidationError."""

        with self.assertRaises(ValidationError):
            models.ThumbnailSize.objects.create(
                tier=models.Tier.objects.create(name="test", thumbnails=False),
                height=200,
            )

        self.assertEqual(models.ThumbnailSize.objects.count(), 0)

    # Tests for image model
    @patch("core.models.uuid.uuid4")
    def test_image_file_name_uuid(self, mock_uuid):
        """Test generating image path."""

        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.image_file_path(None, "example.jpg")

        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")
