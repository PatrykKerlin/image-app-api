"""
Serilizers for image API.
"""

from rest_framework import serializers
from core.models import Image, Thumbnail

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field


class ImageSerializer(serializers.ModelSerializer):
    """Serializer for images."""

    class Meta:
        model = Image
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": True}}


class ThumbnailSerializer(serializers.ModelSerializer):
    """Serializer for thumbnails."""

    height = serializers.SerializerMethodField()
    image_id = serializers.SerializerMethodField()

    class Meta:
        model = Thumbnail
        fields = ["id", "image_id", "height", "thumbnail"]
        read_only_fields = ["id", "image_id"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_height(self, obj):
        return obj.height.height

    @extend_schema_field(OpenApiTypes.INT)
    def get_image_id(self, obj):
        return obj.image.id


class LinkSerializer(serializers.ModelSerializer):
    """Serializer for generating links."""

    time = serializers.IntegerField()

    class Meta:
        model = Image
        fields = ["id", "time"]
        read_only_fields = ["id"]
        extra_kwargs = {"time": {"required": True}}
