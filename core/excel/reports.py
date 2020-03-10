from swutils.date import date_to_rus, iso_to_date

from core.excel.base import Excel


class WorkersDoneExcel(Excel):
    workbook_name = 'Отчет по прошедшим'
    head_static_sizes = {
        '№': 5,
        'Дата осмотра': 13,
        'ФИО': 35,
        'Дата рождения': 13,
        'Пол': 10,
        'Подразделение': 30,
        'Организация': 40,
        'Вид осмотра': 25,
        'Пункты приказа': 18,
        'Стоимость': 10,
        'Заключение профпатолога': 50,
        'Примечание': 50,
    }

    def get_object_rows(self):
        object_rows = []

        for index, obj in enumerate(self.objects, start=1):
            law_items = ', '.join([f"{l_i['name']} прил.{l_i['section']}"
                                   for l_i in obj['prof'][0]['law_items']]) if obj.get('prof') else ''

            object_rows.append(
                [
                    index,
                    date_to_rus(iso_to_date(obj['date'])),
                    obj['client']['fio'],
                    date_to_rus(iso_to_date(obj['client']['birth'])),
                    obj['client']['gender'],
                    obj['prof'][0]['shop'] if obj.get('prof') else '', ', '.join([org['name'] for org in obj['orgs']]),
                    obj['prof'][0]['exam_type'] if obj.get('prof') else '',
                    law_items,
                    obj['total_cost'],
                    obj['prof'][0]['prof_conclusion']['conclusion'] if obj.get('prof') else '',
                    obj['prof'][0].get('note') if obj.get('prof') else ''
                ]
            )

        return object_rows
