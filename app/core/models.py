"""
Database models.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, username, password=None, tier=None, **kwargs):
        """Create, save and return a new user."""

        if not username:
            raise ValidationError("User must have a username.")

        user = self.model(username=username, tier=tier, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password=None, **kwargs):
        """Create, save and return a new admin user."""

        if not username:
            raise ValidationError("User must have a username.")

        user = self.model(
            username=username,
            is_staff=True,
            is_superuser=True,
            **kwargs,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    username = models.CharField(max_length=25, unique=True)
    tier = models.ForeignKey(
        "Tier",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username

    def clean(self):
        if not self.is_staff and not self.is_superuser and not self.tier:
            raise ValidationError(
                "Tier field is required when is_staff and is_superuser are False."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Tier(models.Model):
    """Tier in the system."""

    name = models.CharField(max_length=25, unique=True)
    thumbnail = models.BooleanField(default=True)
    original_size = models.BooleanField(default=False)
    expiring_link = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name:
            raise ValidationError("Tier must have a name.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
