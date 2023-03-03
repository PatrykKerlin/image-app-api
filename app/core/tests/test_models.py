"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.models import Tier


class ModelTests(TestCase):
    """Test models."""

    def test_create_tier_with_name_successfull(self):
        """Test creating a tier with a name is successful."""

        name = "test"
        tier = Tier.objects.create(name=name)

        self.assertEqual(tier.name, name)

    def test_create_tier_without_name_raises_error(self):
        """Test creating a tier without a name raises a ValidationError."""

        with self.assertRaises(ValidationError):
            Tier.objects.create(name="")

    def test_create_user_with_username_successful(self):
        """Test creating a user with a username is successful."""

        username = "example_username"
        password = "test1234"
        user = get_user_model().objects.create_user(
            username=username, password=password, tier=Tier.objects.create(name="test")
        )

        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password, password)

    def test_new_user_without_username_raises_error(self):
        """Test creating a user without a username raises a ValidationError."""

        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                username="", password="test1234", tier=Tier.objects.create(name="test")
            )

    def test_create_superuser(self):
        """Test creating a superuser."""

        user = get_user_model().objects.create_superuser(
            username="example_username",
            password="test1234",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
