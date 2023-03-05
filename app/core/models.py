"""
Database models.
"""

import os
import io

from django.db import models
from django.core.files import File
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.dispatch import receiver

import PIL.Image

from image.utils import image_file_path, image_resize


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
    """User model."""

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
    """Tier model."""

    name = models.CharField(max_length=25, unique=True)
    thumbnails = models.BooleanField(default=True)
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


class ThumbnailSize(models.Model):
    """Thumbnail size model."""

    tier = models.ForeignKey("Tier", on_delete=models.CASCADE)
    height = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tier", "height"], name="unique_tier_height"
            ),
        ]

    def __str__(self):
        return f"{self.tier} - height: {self.height}px"

    def clean(self):
        if not self.tier.thumbnails:
            raise ValidationError("Selected tier does not support thumbnails.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Image(models.Model):
    """Image model."""

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_file_path)
    filename = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.filename

    def __repr__(self):
        return "full_size"

    def delete(self, *args, **kwargs):
        os.remove(self.image.path)
        return super(Image, self).delete(*args, **kwargs)


class Thumbnail(models.Model):
    """Thumbnail model."""

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to=image_file_path)

    def __str__(self):
        return self.thumbnail.path.split("/")[-1]

    def __repr__(self):
        return "thumbnail"

    def delete(self, *args, **kwargs):
        os.remove(self.thumbnail.path)
        return super(Thumbnail, self).delete(*args, **kwargs)


@receiver(models.signals.post_save, sender=Image)
def image_filename_completion(sender, instance, created, **kwargs):
    """Image filename completion in the Image model."""

    if created:
        instance.filename = instance.image.path.split("/")[-1]
        instance.save(update_fields=["filename"])

        heights = ThumbnailSize.objects.filter(
            tier=instance.user.tier,
        ).values_list(
            "height",
            flat=True,
        )
        with open(instance.image.path, "rb") as file:
            image_file = File(file)
            for height in heights:
                img = PIL.Image.open(image_file)
                format = img.format
                resized_img = image_resize(img, height)
                temp_file = io.BytesIO()
                resized_img.save(temp_file, format=format)
                thumbnail = Thumbnail(user=instance.user)
                thumbnail.thumbnail.save("temp_filename.jpg", File(temp_file))
