import re

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware(object):
    def __init__(self, get_response):
        self.exceptions = tuple(re.compile(url) for url in settings.LOGIN_REQUIRED_URLS_EXCEPTIONS)
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:

            for url in self.exceptions:
                if url.match(request.path):
                    return None

            return redirect('{0}?next={1}'.format(
                reverse('login'), request.path
            ))
        elif request.path == reverse('login'):
            return redirect(reverse('core:index'))

        return None
