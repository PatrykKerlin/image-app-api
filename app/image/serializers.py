"""
Serilizers for image API.
"""

from rest_framework import serializers
from core.models import Image

from user.serializers import UserSerializer


class ImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images."""

    user = UserSerializer(required=False)

    class Meta:
        model = Image
        fields = ["id", "user", "image", "filename"]
        read_only_fields = ["id", "filename"]
        extra_kwargs = {"image": {"required": True}}
