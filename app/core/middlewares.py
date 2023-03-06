from django.http import Http404
import time
import base64
from binascii import Error


class ExpireLinkMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self.is_valid_link(request):
            raise Http404("Invalid or expired link.")

        response = self.get_response(request)
        return response

    def is_valid_link(self, request):
        try:
            decrypted_path = base64.urlsafe_b64decode(
                request.path[1:].encode("utf-8")
            ).decode("utf-8")
            expire_time_str = decrypted_path.split("=")[-1]
            if expire_time_str:
                try:
                    expire_time = int(expire_time_str)
                except ValueError:
                    return False
            if expire_time < int(time.time()):
                return False
        except (UnicodeDecodeError, Error):
            pass

        return True
