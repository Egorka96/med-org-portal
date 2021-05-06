import re

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class PasswordChangeMiddleware(object):
    def __init__(self, get_response):
        self.exceptions = tuple(re.compile(url) for url in settings.LOGIN_REQUIRED_URLS_EXCEPTIONS)
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated and request.user.core.need_change_password:

            for url in self.exceptions:
                if url.match(request.path):
                    return None
                elif request.path == reverse('core:password_change'):
                    return None

            return redirect('{0}?next={1}'.format(
                reverse('core:password_change'), request.path
            ))