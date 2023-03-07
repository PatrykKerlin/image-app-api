"""
URL mappings for the image API.
"""

from django.urls import path, include
from rest_framework import routers
from .views import ImageViewSet, ThumbnailViewSet, LinkViewSet

router = routers.DefaultRouter()
router.register("image", ImageViewSet)
router.register("thumbnail", ThumbnailViewSet)
router.register("link", LinkViewSet, basename="link")

app_name = "image"

urlpatterns = [
    path("", include(router.urls)),
]
