"""
Serializers for the user API view.
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

from core.models import User


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""

    username = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate user."""

        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                "Unable to authenticate with provided credentials.",
                code="authorization",
            )

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
        ]
        read_only_fields = ["id"]
