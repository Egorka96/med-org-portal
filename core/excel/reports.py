from swutils.date import date_to_rus, iso_to_date

from core.excel.base import Excel


class WorkersDoneExcel(Excel):
    workbook_name = 'Отчет по прошедшим'

    def __init__(self, *args, show_orgs, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_orgs = show_orgs

    def get_head_static_sizes(self):
        head_static_sizes = {
            '№': 5,
            'Дата осмотра': 13,
            'ФИО': 35,
            'Дата рождения': 13,
            'Пол': 10,
            'Подразделение': 30,
        }

        if self.show_orgs:
            head_static_sizes['Организация'] = 40

        head_static_sizes.update({
            'Вид осмотра': 25,
            'Пункты приказа': 18,
            'Стоимость': 10,
            'Заключение профпатолога': 50,
            'Примечание': 50,
        })
        return head_static_sizes

    def get_object_rows(self):
        object_rows = []

        for index, obj in enumerate(self.objects, start=1):
            law_items = ', '.join([f"{l_i['name']} прил.{l_i['section']}"
                                   for l_i in obj['prof'][0]['law_items']]) if obj.get('prof') else ''

            row = [
                index,
                date_to_rus(iso_to_date(obj['date'])),
                obj['client']['fio'],
                date_to_rus(iso_to_date(obj['client']['birth'])),
                obj['client']['gender'],
                obj['prof'][0]['shop'] if obj.get('prof') else '',
            ]

            if self.show_orgs:
                row.append(', '.join([org['name'] for org in obj['orgs']]))

            row.extend([
                ', '.join(obj['main_services']),
                law_items,
                obj['total_cost'],
                obj['prof'][0]['prof_conclusion']['conclusion'] if obj.get('prof') else '',
                obj['prof'][0].get('note') if obj.get('prof') else ''
            ])
            object_rows.append(row)

        return object_rows
