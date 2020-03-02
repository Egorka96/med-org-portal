from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin as DjangoFormMixin


class FormMixin(DjangoFormMixin):
    data_method = None

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        kwargs.update({
            'data': getattr(self.request, self.data_method.upper() if self.data_method else 'GET') or None,
            'files': self.request.FILES or None
        })
        return kwargs


class BreadcrumbsMixin(ContextMixin):

    def get_breadcrumbs(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class TitleMixin(ContextMixin):
    title = None

    def get_title(self):
        return self.title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_title()
        return context