"""
Django command to fill the database with basic tiers data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.models import Tier, ThumbnailSize


class Command(BaseCommand):
    """Django command to fill the database with basic tiers data."""

    def handle(self, *args, **kwargs):
        """Entrypoint for command."""

        if (get_user_model().objects.filter(is_superuser=True).count()) == 0:
            get_user_model().objects.create_superuser(
                username="admin",
                password="admin",
            )
        if Tier.objects.count() == 0:
            basic = Tier.objects.create(name="Basic")
            premium = Tier.objects.create(name="Premium", original_size=True)
            enterprise = Tier.objects.create(
                name="Enterprise", original_size=True, expiring_link=True
            )
            ThumbnailSize.objects.create(tier=basic, height=200)
            ThumbnailSize.objects.create(tier=premium, height=200)
            ThumbnailSize.objects.create(tier=premium, height=400)
            ThumbnailSize.objects.create(tier=enterprise, height=200)
            ThumbnailSize.objects.create(tier=enterprise, height=400)

        self.stdout.write(self.style.WARNING("Base setup ready!"))
