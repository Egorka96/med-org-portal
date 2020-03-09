from core.excel.base import Excel


class WorkersDoneExcel(Excel):
    workbook_name = 'Отчет по прошедшим'
    headers = ['№', 'Дата осмотра', 'ФИО', 'Дата рождения', 'Пол', 'Подразделение', 'Организация', 'Вид осмотра',
               'Пункты приказа', 'Стоимость', 'Заключение профпатолога', 'Примечание']

    def write_object(self, obj):
        sheet = self.get_sheet()

        current_row = self.get_current_row()
        sheet.cell(current_row, 2, obj['date'])
        sheet.cell(current_row, 3, obj['client']['fio'])
        sheet.cell(current_row, 4, obj['client']['birth'])
        sheet.cell(current_row, 5, obj['client']['gender'])
        sheet.cell(current_row, 6, obj['prof'][0]['shop'] if obj.get('prof') else '')
        sheet.cell(current_row, 7, ', '.join([org['name'] for org in obj['orgs']]))
        sheet.cell(current_row, 8, obj['prof'][0]['exam_type'] if obj.get('prof') else '')
        sheet.cell(current_row, 9, ', '.join([f"{l_i['name']} прил.{l_i['section']}"
                                              for l_i in obj['prof'][0]['law_items']]) if obj.get('prof') else '')
        sheet.cell(current_row, 10, obj['total_cost'])
        sheet.cell(current_row, 11, obj['prof'][0]['prof_conclusion']['conclusion'] if obj.get('prof') else '')
        sheet.cell(current_row, 12, obj['prof'][0].get('note') if obj.get('prof') else '')
