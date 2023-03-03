"""
Django command to fill the database with basic tiers data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.models import Tier


class Command(BaseCommand):
    """Django command to fill the database with basic tiers data."""

    def handle(self, *args, **kwargs):
        """Entrypoint for command."""

        Tier.objects.create(
            name="Basic",
        )
        Tier.objects.create(
            name="Premium",
            original_size=True,
        )
        Tier.objects.create(
            name="Enterprise",
            original_size=True,
            expiring_link=True,
        )
        get_user_model().objects.create_superuser(
            username="admin",
            password="admin",
        )

        self.stdout.write(self.style.WARNING("Base setup ready!"))
