from swutils.date import date_to_rus, iso_to_date

from core.excel.base import Excel
from mis.service_client import Mis


class WorkersDoneExcel(Excel):
    workbook_name = 'Отчет по прошедшим'

    def __init__(self, *args, show_orgs: bool, show_cost: bool, mis_request_path: str, filter_params, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_orgs = show_orgs
        self.show_cost = show_cost
        self.mis_request_path = mis_request_path
        self.filter_params = filter_params

        if not self.objects:
            self.objects = self.get_objects()

        self.use_lmk = any(obj.get('lmk') for obj in self.objects)

    def get_objects(self):
        objects = []

        # выкачиваем из МИС данные для отчета пока не кончатся
        page = 1
        while True:
            response_data = Mis().request(
                path=self.mis_request_path + f"?page={page}",
                user=self.background_task.user,
                params=self.filter_params,
            )
            objects.extend(response_data['results'])
            if not response_data['next']:
                break

            # сохраним прогресс выполнения
            if self.background_task:
                percent = (50 * page) * 100 / response_data['count']
                description = f"Обработано {page * 50} объектов из {response_data['count']}"

                self.save_background_task_progress(percent, description)

            page += 1

        return objects

    def get_head_static_sizes(self):
        head_static_sizes = {
            '№': 5,
            'Дата осмотра': 13,
            'ФИО': 35,
            'Дата рождения': 13,
            'Пол': 10,
            'Подразделение': 30,
            'Должность': 30,
        }

        if self.show_orgs:
            head_static_sizes['Организация'] = 40

        head_static_sizes.update({
            'Вид осмотра': 25,
            'Пункты приказа': 18,
        })

        if self.show_cost:
            head_static_sizes['Стоимость'] = 10

        head_static_sizes['Заключение профпатолога'] = 50
        if self.use_lmk:
            head_static_sizes.update({
                'Номер бланка ЛМК': 20,
                'Дата бланка ЛМК': 12,
                'Вид аттестации': 15,
                'Дата аттестации': 12
            })

        head_static_sizes['Примечание'] = 50
        return head_static_sizes

    def get_object_rows(self):
        object_rows = []

        for index, obj in enumerate(self.objects, start=1):
            law_items = ', '.join([l_i['display'] for l_i in obj['prof'][0]['law_items']]) if obj.get('prof') else ''

            row = [
                index,
                ', '.join([date_to_rus(iso_to_date(date)) for date in obj['dates']]),
                obj['client']['fio'],
                date_to_rus(iso_to_date(obj['client']['birth'])),
                obj['client']['gender'],
                obj['prof'][0]['shop'] if obj.get('prof') else '',
                ', '.join(obj['posts']),
            ]
            if self.show_orgs:
                row.append(', '.join([org['legal_name'] or org['name']
                                      for org in obj['orgs']]) if obj.get('orgs') else '')

            row.extend([
                ', '.join(self.get_obj_main_services(obj)),
                law_items,
            ])
            if self.show_cost:
                row.append(obj['total_cost'])

            row.append(obj['prof'][0]['prof_conclusion']['conclusion'] if obj.get('prof') else '')
            if self.use_lmk:
                row.extend([
                    ', '.join(f"{b['number']} {b['reg_number']}" for b in obj['lmk_blanks']),
                    ', '.join(date_to_rus(iso_to_date(b['date'])) for b in obj['lmk_blanks']),
                    ', '.join('Первичная' if att['is_first'] else 'Периодическая' for att in obj['lmk_attestations']),
                    ', '.join(date_to_rus(iso_to_date(att['date'])) for att in obj['lmk_attestations']),
                ])

            row.append(obj['prof'][0].get('note') if obj.get('prof') else '')
            object_rows.append(row)

        return object_rows

    def get_obj_main_services(self, obj):
        main_services = []

        for app in ['prof', 'lmk', 'certificate', 'heal']:
            app_orders = obj[app]
            for o in app_orders:
                main_services.append(o.get('main_services'))

        return main_services
