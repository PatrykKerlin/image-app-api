"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_username_successful(self):
        """Test creating a user with a username is successful."""

        username = "example_username"
        password = "test1234"
        user = get_user_model().objects.create(
            username=username,
            password=password,
        )

        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password, password)

    def test_new_user_without_username_raises_error(self):
        """Test creating a user without a username raises a ValueError."""

        with self.assertRaises(ValueError):
            get_user_model().objects.create(
                username="",
                password="test1234",
            )

    def test_create_superuser(self):
        """Test creating a superuser."""

        user = get_user_model().objects.create_superuser(
            username="example_username",
            password="test1234",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
