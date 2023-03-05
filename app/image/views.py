"""
Views for the image API.
"""

from rest_framework import viewsets, mixins

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.models import Image
from .serializers import ImageSerializer


class ImageViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if not request.user.is_superuser and not request.user.tier.original_size:
            response.data.pop("image", None)
            return response

        return response
