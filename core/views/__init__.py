from django.http import HttpResponse
from django.shortcuts import render


def response_forbidden_handler(request, exception=None):
    return HttpResponse(render(request, 'core/errors/403.html'), status=403)


def response_not_found_error_handler(request, exception=None):
    return HttpResponse(render(request, 'core/errors/404.html'), status=404)


def response_server_error_handler(request, exception=None):
    return HttpResponse(render(request, 'core/errors/500.html'), status=500)
