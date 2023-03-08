"""
Database models.
"""

import os
import io
import uuid
import datetime

from django.db import models
from django.core.validators import validate_image_file_extension
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


def image_file_path(instance, filename):
    """Generate file path for new image"""

    extension = os.path.splitext(filename)[1]
    user_id = instance.user.id
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    unique_id = str(uuid.uuid4()).split("-")[-1]
    filename = f"{user_id}_{timestamp}_{unique_id}_{repr(instance)}{extension}"

    return os.path.join("uploads", "images", str(user_id), filename)


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

    tier = models.ForeignKey(
        "Tier",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
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
    image = models.ImageField(
        upload_to=image_file_path, validators=[validate_image_file_extension]
    )

    def __str__(self):
        return self.image.path.split("/")[-1]

    def __repr__(self):
        return "full_size"

    def delete(self, *args, **kwargs):
        for thumb in Thumbnail.objects.filter(image=self):
            thumb.delete()
        os.remove(self.image.path)
        return super(Image, self).delete(*args, **kwargs)


class Thumbnail(models.Model):
    """Thumbnail model."""

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    image = models.ForeignKey("Image", on_delete=models.CASCADE)
    height = models.ForeignKey("ThumbnailSize", on_delete=models.CASCADE)
    thumbnail = models.ImageField(
        upload_to=image_file_path, validators=[validate_image_file_extension]
    )

    def __str__(self):
        return self.thumbnail.path.split("/")[-1]

    def __repr__(self):
        return "thumbnail"

    def delete(self, *args, **kwargs):
        os.remove(self.thumbnail.path)
        return super(Thumbnail, self).delete(*args, **kwargs)


@receiver(models.signals.post_save, sender=Image)
def image_filename_completion(sender, instance, created, **kwargs):
    """Automatic generation of thumbnails."""

    if created:
        if instance.user.is_superuser or instance.user.is_staff:
            height_list = ThumbnailSize.objects.values_list(
                "height",
                flat=True,
            ).distinct()
        elif instance.user.tier.thumbnails:
            height_list = ThumbnailSize.objects.filter(
                tier=instance.user.tier,
            ).values_list(
                "height",
                flat=True,
            )

        if height_list:
            ext = instance.image.path.split(".")[-1]
            with open(instance.image.path, "rb") as file:
                image_file = File(file)
                for height in height_list:
                    if instance.user.tier:
                        thumbnail_size_obj = ThumbnailSize.objects.get(
                            tier=instance.user.tier,
                            height=height,
                        )
                    else:
                        thumbnail_size_obj = ThumbnailSize.objects.filter(
                            height=height,
                        ).last()
                    img = PIL.Image.open(image_file)
                    format = img.format
                    original_width, original_height = img.size
                    ratio = original_height / height
                    width = int(original_width / ratio)
                    resized_img = img.resize((width, height))
                    temp_file = io.BytesIO()
                    resized_img.save(temp_file, format=format)
                    resized_img.seek(0)
                    thumbnail = Thumbnail(
                        user=instance.user, height=thumbnail_size_obj, image=instance
                    )
                    thumbnail.thumbnail.save(f"temp_filename.{ext}", File(temp_file))
