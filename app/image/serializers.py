"""
Serilizers for image API.
"""

from rest_framework import serializers
from core.models import Image, Thumbnail, ThumbnailSize


class ImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images."""

    # user = UserSerializer(required=False)

    class Meta:
        model = Image
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": True}}


class ThumbnailSizeSerializer(serializers.ModelSerializer):
    """Serializer for thumbnail sizes."""

    class Meta:
        model = ThumbnailSize
        fields = ["height"]
        # read_only_fields = ["id", "filename"]
        # extra_kwargs = {"image": {"required": True}}


class ThumbnailSerializer(serializers.ModelSerializer):
    """Serializer for thumbnails."""

    size = ThumbnailSizeSerializer(required=False)

    class Meta:
        model = Thumbnail
        fields = ["id", "size", "thumbnail"]
        # read_only_fields = ["id", "filename"]
        # extra_kwargs = {"image": {"required": True}}


class LinkSerializer(serializers.ModelSerializer):
    """Serializer for generating links."""

    # user = UserSerializer(required=False)
    time = serializers.IntegerField()

    class Meta:
        model = Image
        fields = ["id", "time"]
        # read_only_fields = ["id"]
        # extra_kwargs = {"time": {"required": True}}
