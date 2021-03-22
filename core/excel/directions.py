from core.excel.base import Excel
from mis.service_client import Mis
from swutils.date import date_to_rus, iso_to_date


class DirectionsExcel(Excel):
    workbook_name = 'Направления'

    def __init__(self, *args, show_orgs: bool, mis_request_path: str, filter_params, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_orgs = show_orgs
        self.mis_request_path = mis_request_path
        self.filter_params = filter_params


        if not self.objects:
            self.objects = self.get_objects()

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
            'ФИО': 35,
            'Дата рождения': 15,
            'Пол': 15,
        }

        if self.show_orgs:
            head_static_sizes['Организация'] = 30

        head_static_sizes.update({
            'Подразделение': 20,
            'Пункты приказа': 20,
            'Время действия': 30,
            'Дата прохождения': 20
        })

        return head_static_sizes

    def get_object_rows(self):
        object_rows = []

        for index, obj in enumerate(self.objects, start=1):
            law_items = ', '.join([f"{l_i['name']} прил.{l_i['section']}"
                                   for l_i in obj['law_items']]) if obj.get('law_items') else ''
            confirm_dt = [dt for dt in obj['confirm_dt']] if obj.get('confirm_dt') else  '-'

            row = [
                index,
                ' '.join([obj['last_name'], obj['first_name'], obj['middle_name']]),
                date_to_rus(iso_to_date(obj['birth'])),
                obj['gender'],
            ]

            if self.show_orgs:
                row.append(obj['org']['legal_name'])

            row.extend([
                obj['shop'],
                law_items,
                ' '.join([f"с {date_to_rus(iso_to_date(obj['date_from']))} по {date_to_rus(iso_to_date(obj['date_to']))}"]),
                confirm_dt
            ])

            object_rows.append(row)

        return object_rows




