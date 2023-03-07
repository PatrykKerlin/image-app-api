import time
import base64
from binascii import Error

from django.shortcuts import redirect
from django.http import Http404


class ExpiringLinkMiddleware:
    """Middleware for handling expiring links."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.GET.get("exp") == "1":
            if link := self.decode_link(request):
                return redirect(link)
            raise Http404("Invalid or expired link.")

        response = self.get_response(request)
        return response

    def decode_link(self, request):
        """URL decoding method."""
        try:
            decrypted_path = base64.urlsafe_b64decode(
                request.path[1:].encode("utf-8")
            ).decode("utf-8")
            expire_time_str = decrypted_path.split("=")[-1]
            expire_time = int(expire_time_str)
            if expire_time < time.time():
                return False
            return decrypted_path.split("?")[0]
        except (UnicodeDecodeError, Error, ValueError):
            return False
