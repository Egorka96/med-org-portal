from tempfile import NamedTemporaryFile

import re
from django.http import HttpResponse

from openpyxl import Workbook

from swutils.string import transliterate


class Excel:
    workbook_name = 'Отчет'
    headers = []

    def __init__(self, title=None, objects: list = None):
        self.title = title
        self.objects = objects

        self._workbook = None
        self._sheet = None
        self._row = 1

    def create_workbook(self):
        workbook = self.get_workbook()

        self.write_header()
        self.write_table_header()
        self.write_objects()

        file_name = transliterate(self.get_workbook_name(), space='_')
        # очистим имя файла от небуквенных символов
        file_name = re.sub("[^\\w]", "", file_name)
        file_name += '.xlsx'

        with NamedTemporaryFile() as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            response = HttpResponse(content_type='application/ms-excel', content=tmp.read())
            response['Content-Disposition'] = 'attachment; filename=%s' % file_name
            return response

    def get_workbook(self):
        if not self._workbook:
            self._workbook = Workbook()
        return self._workbook

    def get_sheet(self):
        sheet = self.get_workbook().active
        sheet.title = self.get_sheet_name()
        return sheet

    def get_workbook_name(self):
        return self.workbook_name

    def get_sheet_name(self):
        return self.get_workbook_name()[:30]

    def get_headers(self):
        return self.headers or []

    def get_current_row(self):
        return self._row

    def add_current_row(self):
        self._row += 1

    def write_header(self):
        """ Заголовок над таблицей отчета """
        sheet = self.get_sheet()

        if not self.title:
            return

        title_cell = sheet.cell(self.get_current_row(), 1, self.title)
        # todo: добавление стилей https://openpyxl.readthedocs.io/en/stable/styles.html#cell-styles

        self.add_current_row()

    def write_table_header(self):
        """ Шапка таблицы """
        sheet = self.get_sheet()
        headers = self.get_headers()

        current_row = self.get_current_row()
        for col, header in enumerate(headers, start=1):
            sheet.cell(current_row, col, header)

        self.add_current_row()

    def write_objects(self):
        sheet = self.get_sheet()

        for i, obj in enumerate(self.objects, start=1):
            sheet.cell(self.get_current_row(), 1, i)
            self.write_object(obj)
            self.add_current_row()

    def write_object(self, obj):
        raise NotImplementedError()
