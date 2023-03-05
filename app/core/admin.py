"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""

    ordering = ["id"]
    list_display = ["username"]
    list_filter = ("username", "tier", "is_active", "is_staff", "is_superuser")

    fieldsets = (
        (None, {"fields": ("username", "tier", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide"),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "tier",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tier)
admin.site.register(models.ThumbnailSize)
admin.site.register(models.Image)
admin.site.register(models.Thumbnail)
