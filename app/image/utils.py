"""
Utils for images managing.
"""

import os
import uuid
import datetime


def image_file_path(instance, filename):
    """Generate file path for new recipe image"""

    extension = os.path.splitext(filename)[1]
    user_id = instance.user.id
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    unique_id = str(uuid.uuid4()).split("-")[-1]
    filename = f"{user_id}_{timestamp}_{unique_id}_{repr(instance)}{extension}"

    return os.path.join("uploads", "images", str(user_id), filename)


def image_resize(img, new_height):
    """Resize image."""

    original_width, original_height = img.size
    ratio = original_height / new_height
    new_width = int(original_width / ratio)
    resized_img = img.resize((new_width, new_height))

    return resized_img
