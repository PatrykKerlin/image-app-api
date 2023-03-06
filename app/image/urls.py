"""
URL mappings for the image API.
"""

from django.urls import path, include
from rest_framework import routers
from .views import ImageViewSet, ThumbnailViewSet, LinkViewSet

router = routers.DefaultRouter()
router.register("images", ImageViewSet)
router.register("thumbnails", ThumbnailViewSet)
router.register("link", LinkViewSet)

app_name = "image"

urlpatterns = [
    path("", include(router.urls)),
    # path("link/", LinkViewSet.as_view({"get": "get_expiring_link"}), name="link"),
]
