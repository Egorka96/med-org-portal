from tempfile import NamedTemporaryFile

import re
from django.http import HttpResponse

from openpyxl import Workbook
from openpyxl.worksheet.table import Table
from openpyxl.styles import Font, Border, Side

from swutils.string import transliterate


class Excel:
    alphabet = [chr(code) for code in range(65, 91)]

    workbook_name = 'Отчет'
    headers = []

    head_static_sizes = {
        '№': 10,
    }

    def __init__(self, title=None, objects: list = None):
        self.title = title
        self.objects = objects

        self._workbook = None
        self._sheet = None
        self._row = 1

    def create_workbook(self):
        workbook = self.get_workbook()

        self.write_header()
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
        return list(self.get_head_static_sizes().keys()) or []

    def get_head_static_sizes(self):
        return self.head_static_sizes or {}

    def get_col_address(self, number: int) -> str:
        second_rank = number % len(self.alphabet)
        first_rank = number // len(self.alphabet)

        address = ''
        if first_rank:
            address = self.get_col_address(first_rank - 1)

        return address + self.alphabet[second_rank]

    def get_cell_address(self, row_number: int, col_number: int) -> str:
        """ Возвращает физический адрес ячейки типа А1 """
        return '%s%s' % (self.get_col_address(col_number), row_number + 1)

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

        bold_font = self.get_bold_font()
        self.set_font_size(bold_font, 14)
        title_cell.font = bold_font

        sheet.row_dimensions[self.get_current_row()].height = 30

        self.add_current_row()

    def write_objects(self):
        sheet = self.get_sheet()

        object_rows = self.get_object_rows()
        sheet.append(self.get_headers())

        for row in object_rows:
            sheet.append(row)

        current_row = self.get_current_row()

        for col_num, header in zip(range(1, len(self.get_headers())), self.get_headers()):
            cell = sheet[self.get_cell_address(current_row - 1, col_num)]
            cell.font = self.get_bold_font()

            sheet.column_dimensions[self.get_col_address(col_num - 1)].width = self.get_head_static_sizes().get(header, 30)

        cell_table_start = self.get_cell_address(current_row - 1, 1)
        cell_table_finish = self.get_cell_address(current_row - 1, len(self.get_headers()) - 1)

        tab = Table(
            displayName="Table1",
            ref=f"{cell_table_start}:{cell_table_finish}"
        )
        sheet.add_table(tab)

        for row in range(current_row, len(self.objects) + current_row + 1):
            for col in range(1, len(self.get_headers()) + 1):
                sheet.cell(row=row, column=col).border = self.get_border()

    def get_object_rows(self):
        raise NotImplementedError()

    @staticmethod
    def get_bold_font():
        return Font(bold=True)

    @staticmethod
    def get_border():
        return Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

    @staticmethod
    def set_font_size(font, size):
        font.sz = size
        return font
