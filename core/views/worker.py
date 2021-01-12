from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic.base import View
from swutils.string import transliterate

import core.generic.mixins
import core.generic.views

from core import forms
from mis.document import Document
from mis.service_client import Mis
from mis.worker import Worker


class Search(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.mixins.RestListMixin,
             core.generic.views.ListView):
    title = 'Сотрудники'
    form_class = forms.WorkerSearch
    paginate_by = 100
    permission_required = 'core.view_worker'
    template_name = 'core/workers/list.html'
    mis_request_path = Mis.WORKERS_LIST_URL
    load_without_params = True

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            (self.title, ''),
        ]

    def process_response_results(self, objects):
        return [Worker.get_from_dict(obj) for obj in objects]


class DocumentPrint(PermissionRequiredMixin, View):
    permission_required = 'core.view_worker'

    def get(self, request, *args, **kwargs):
        worker_mis_id = self.request.GET.get('worker_mis_id')
        document_link = self.request.GET.get('document_link')

        if not worker_mis_id:
            return HttpResponse("Не указан сотрудник, по которому необходимо печатать документ.")

        worker = Worker.get(worker_id=worker_mis_id)
        file_name = transliterate(str(worker))
        pdf_content = Document.get_content(path=document_link)

        # сгенерируем HttpResponse-объект с pdf
        response = HttpResponse(pdf_content, content_type="application/pdf")
        response['Content-Disposition'] = 'filename=%s.pdf' % file_name
        return response
