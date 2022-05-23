from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, PasswordChangeView, logout_then_login
from django.views.generic import TemplateView

import core.urls
import help.urls
import background_tasks.urls
from core.views.login import Login

urlpatterns = [
    path('', include(core.urls, namespace='core')),
    path('help/', include(help.urls, namespace='help')),
    path('background_tasks/', include(background_tasks.urls, namespace='background_tasks')),
    path('admin/', admin.site.urls),

    path('login/', Login.as_view(), name='login'),
    path('logout/', logout_then_login, {'login_url': '/login/?next=/'}, name='logout'),

    path('password_change/', PasswordChangeView.as_view(template_name='core/password_change.html',
                                                        success_url='/logout/'), name='password_change'),
]

handler403 = 'core.views.response_forbidden_handler'
handler404 = 'core.views.response_not_found_error_handler'
handler500 = 'core.views.response_server_error_handler'

if settings.DEBUG:
    urlpatterns += static('node_modules', document_root=settings.BASE_DIR + '/node_modules')
    urlpatterns += static('media', document_root=settings.MEDIA_ROOT)

    urlpatterns = [
        # для отладки страниц ошибок
        path('403/', TemplateView.as_view(template_name='core/errors/403.html')),
        path('404/', TemplateView.as_view(template_name='core/errors/404.html')),
        path('500/', TemplateView.as_view(template_name='core/errors/500.html')),
    ] + urlpatterns
