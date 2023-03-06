"""
Views for the image API.
"""

import time
import base64

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes


from rest_framework import status

from rest_framework import viewsets, mixins

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from core.models import Image, Thumbnail
from .serializers import ImageSerializer, ThumbnailSerializer, LinkSerializer


def check_user_acces_to_original_image(request):
    """"""
    if (
        request.user.is_superuser
        or request.user.is_staff
        or request.user.tier.original_size
    ):
        return True
    return False


def check_user_acces_to_thumbnails(request):
    """"""
    if (
        request.user.is_superuser
        or request.user.is_staff
        or request.user.tier.thumbnails
    ):
        return True
    return False


def check_user_acces_to_expiring_link(request):
    """"""
    if (
        request.user.is_superuser
        or request.user.is_staff
        or request.user.tier.expiring_link
    ):
        return True
    return False


class ImageViewSet(
    mixins.RetrieveModelMixin,
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

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        if not check_user_acces_to_original_image(request):
            for path in response.data:
                path["image"] = path["image"].split("/")[-1]

            return response

        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        if not check_user_acces_to_original_image(request):
            response.data["image"] = response.data["image"].split("/")[-1]
            return response

        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if not check_user_acces_to_original_image(request):
            response.data["image"] = response.data["image"].split("/")[-1]

            return response

        return response


class ThumbnailViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ThumbnailSerializer
    queryset = Thumbnail.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thumbnail.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        if check_user_acces_to_thumbnails(request):
            return response

        return Response(status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if check_user_acces_to_thumbnails(request):
            return response

        return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        if check_user_acces_to_thumbnails(request):
            return response

        return Response(status=status.HTTP_403_FORBIDDEN)


@extend_schema_view(
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                "time",
                OpenApiTypes.INT,
                description="Link expiring time.",
            ),
        ]
    )
)
class LinkViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = LinkSerializer
    queryset = Image.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        if check_user_acces_to_expiring_link:
            image = self.get_object()
            if image:
                if request.GET.get("time"):
                    request_time = request.GET.get("time")
                    try:
                        request_time_int = int(request_time)
                        if request_time_int < 300 or request_time_int > 30000:
                            raise ValueError
                    except ValueError:
                        return Response(
                            {"time": "the value must be between 300 and 30000"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    request_time = 300
                exp_time = int(time.time()) + request_time_int
                url_with_exp = f"{image.image.url}?expires={exp_time}"
                encrypted_path = base64.urlsafe_b64encode(
                    url_with_exp.encode("utf-8")
                ).decode("utf-8")
                encrypted_url_with_exp = (
                    f"http://{request.META['HTTP_HOST']}/{encrypted_path}"
                )

                return Response(
                    {
                        "url": encrypted_url_with_exp,
                        "expiers_in": int(request_time),
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_403_FORBIDDEN)
