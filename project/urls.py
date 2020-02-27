from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import core.urls


urlpatterns = [
    path('', include(core.urls, namespace='core')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static('node_modules', document_root=settings.BASE_DIR + '/node_modules')
    urlpatterns += static('media', document_root=settings.MEDIA_ROOT)
