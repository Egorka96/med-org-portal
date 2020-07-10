from django.http import Http404, HttpResponse

import logging

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView

import core.generic.views
import core.generic.mixins

from background_tasks import models
from background_tasks import forms
from background_tasks import filters
from background_tasks import datatools

logger = logging.getLogger('db')


class Search(core.generic.mixins.FormMixin, core.generic.views.ListView):
    title = 'Фоновые задачи'
    template_name = 'background_tasks/task/search.html'
    model = models.Task
    form_class = forms.TaskSearch
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()

        form = self.get_form()
        if form.is_valid():
            qs = filters.Task(data=form.cleaned_data, queryset=qs).qs

        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)

        return qs.order_by('-created_dt')


class Detail(DetailView):
    template_name = 'background_tasks/task/detail.html'
    model = models.Task

    # def get_object(self):
    #     return models.Task.objects.get(pk=self.kwargs['pk'])

    def get_title(self):
        return str(self.get_object())

    def get_success_url(self):
        return self.request.GET.get('next') or reverse('background_tasks:task_search')

    # def get_context_data(self, **kwargs):
    #     c = super().get_context_data(**kwargs)
    #     c['object'] = self.get_object()
    #     return c


class Cancel(UpdateView):
    model = models.Task

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not self.request.user.is_superuser and obj.user != self.request.user:
            raise Http404()
        return obj

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        datatools.cancel_task(task)
        if request.is_ajax():
            return HttpResponse('ok')
        else:
            return redirect(self.get_success_url())

    def get_success_url(self):
        return self.request.GET.get('next') \
               or reverse('background_tasks:task_info', kwargs={'pk': self.get_object().id})


class Restart(UpdateView):
    model = models.Task

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not self.request.user.is_superuser and obj.user != self.request.user:
            raise Http404()
        return obj

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        datatools.restart_task(task)
        if request.is_ajax():
            return HttpResponse('ok')
        else:
            return redirect(self.get_success_url())

    def get_success_url(self):
        return self.request.GET.get('next') \
               or reverse('background_tasks:task_info', kwargs={'pk': self.get_object().id})
