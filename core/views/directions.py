import json
from typing import Optional, Dict, List

import requests
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse

import core.generic.mixins
import core.generic.views

from core import forms


class Search(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.mixins.RestListMixin,
             core.generic.views.ListView):
    template_name = 'core/directions/list.html'
    form_class = forms.DirectionSearch
    title = 'Направления'
    permission_required = 'core.view_direction'
    paginate_by = 50

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object_list: Optional[List[Dict]] = None

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            (self.title, ''),
        ]

    def get_queryset(self):
        if self.get_objects() is None:
            return []
        else:
            return self.get_objects()

    def get_objects(self):
        if self.object_list is None:
            form = self.get_form()
            if form.is_valid():
                filter_params = dict(self.request.GET)
                filter_params['group_clients'] = True

                if self.request.user.core.org_ids and not filter_params.get('orgs'):
                    filter_params.update({
                        'orgs': json.loads(self.request.user.core.org_ids)
                    })

                url = settings.MIS_URL + '/api/pre_record/'
                headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

                response = requests.get(url=url, params=filter_params, headers=headers)
                response.raise_for_status()

                response_data = response.json()
                self.object_list = response_data['results']
                self.count = response_data['count']
                self.have_next = bool(response_data['next'])
                self.have_previous = bool(response_data['previous'])
            else:
                self.object_list = []
                self.count = 0

        return self.object_list

    def get_context_data(self, **kwargs):
        self.get_objects()
        c = super().get_context_data(**kwargs)

        user_orgs = self.request.user.core.get_orgs()
        c['show_orgs'] = False if user_orgs and len(user_orgs) < 2 else True

        if self.object_list:
            c['object_list'] = self.object_list

        return c
