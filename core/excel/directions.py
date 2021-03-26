from core.excel.base import Excel
from mis.direction import Direction
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
            objects.extend([Direction.dict_to_obj(obj) for obj in response_data['results']])
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
            'Страховой номер': 20
        }

        if self.show_orgs:
            head_static_sizes['Организация'] = 40

        head_static_sizes.update({
            'Должность': 30,
            'Подразделение': 30,
            'Вид осмотра': 20,
            'Пункты приказа': 30,
            'Время действия': 30,
            'Дата прохождения': 20
        })

        return head_static_sizes

    def get_object_rows(self):
        object_rows = []

        for index, obj in enumerate(self.objects, start=1):
            law_items = ', '.join([str(l_i)
                                   for l_i in obj.law_items]) if obj.law_items else ''
            confirm_dt = date_to_rus(obj.confirm_date) if date_to_rus(obj.confirm_date) else '-'
            insurance_policy = obj.insurance_policy.number if obj.insurance_policy else ''

            row = [
                index,
                obj.get_fio(),
                date_to_rus(obj.birth),
                obj.gender,
                insurance_policy
            ]

            if self.show_orgs:
                row.append(obj.org.legal_name if obj.org else '')

            row.extend([
                obj.post,
                obj.shop,
                obj.exam_type,
                law_items,
                ' '.join([f"с {date_to_rus(obj.from_date)} по {date_to_rus(obj.to_date)}"]),
                confirm_dt
            ])

            object_rows.append(row)

        return object_rows




