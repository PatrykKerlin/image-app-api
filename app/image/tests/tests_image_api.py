"""
Tests for the image API.
"""

import os
import tempfile

from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models


IMAGE_URL = reverse("image:image-list")


class ImageUploadAPITests(TestCase):
    """Test the image upload API."""

    def setUp(self):
        """Create and return a user and a client."""
        self.client = APIClient()
        tier = models.Tier.objects.create(name="Test tier 2 thumbs")
        models.ThumbnailSize.objects.create(tier=tier, height=200)
        models.ThumbnailSize.objects.create(tier=tier, height=400)
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test1234",
            tier=tier,
        )

    def tearDown(self):
        """Clean up after test."""

        if models.Image.objects.filter(user=self.user).exists():
            models.Image.objects.get(user=self.user).delete()
        while models.Thumbnail.objects.filter(user=self.user).exists():
            models.Thumbnail.objects.filter(user=self.user).first().delete()

    def test_upload_image_authorized_user(self):
        """Test uploading an image by authorized user."""

        self.client.force_authenticate(self.user)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {
                "image": image_file,
                "username": self.user.username,
            }
            response = self.client.post(IMAGE_URL, payload, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            os.path.exists(models.Image.objects.get(user=self.user).image.path)
        )

    def test_upload_image_unauthorized_user(self):
        """Test uploading an image by unauthorized user."""

        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {
                "image": image_file,
                "username": self.user.username,
            }
            response = self.client.post(IMAGE_URL, payload, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(models.Image.objects.count(), 0)

    def test_upload_image_bad_request(self):
        """Test uploading invalid image."""

        self.client.force_authenticate(self.user)

        payload = {
            "image": "not_an_image",
            "username": self.user.username,
        }
        response = self.client.post(IMAGE_URL, payload, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_images(self):
        """Test list of uploaded images."""

        self.client.force_authenticate(self.user)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {
                "image": image_file,
                "username": self.user.username,
            }
            self.client.post(IMAGE_URL, payload, format="multipart")

        response = self.client.get(IMAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            os.path.exists(models.Image.objects.get(user=self.user).image.path)
        )

    def test_creating_thumbnails(self):
        """Test creating thumbnails for uploaded image."""

        self.client.force_authenticate(self.user)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {
                "image": image_file,
                "username": self.user.username,
            }
            self.client.post(IMAGE_URL, payload, format="multipart")

        response = self.client.get(IMAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Thumbnail.objects.count(), 2)
