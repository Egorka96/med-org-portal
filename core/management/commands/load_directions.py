import datetime
import logging
from time import sleep
from requests import HTTPError

from django.conf import settings
from django.core.management import BaseCommand
from djutils.management.commands import add_date_from_to_arguments, process_date_from_to_options
from django.utils.timezone import now
from swutils.date import iso_to_datetime
import sw_logger.consts

import mis.direction
from core import models

logger = logging.getLogger('db')


class Command(BaseCommand):
    args = ''
    help = 'Выгрузка направлений из мис'

    def add_arguments(self, parser):
        parser.add_argument(
            '--infinitely',
            '-i',
            dest='infinitely',
            action='store_true',
            default=False,
            help='Бесконечно проверять есть ли что отправить',
        )
        add_date_from_to_arguments(parser)

    def handle(self, *args, **options):
        origin_dt_from, origin_dt_to = process_date_from_to_options(options, to_datetime=True)
        dt_from = origin_dt_from
        dt_to = origin_dt_to

        try:
            while True:
                if not dt_to:
                    dt_to = now()
                if not dt_from:
                    dt_from_iso = models.Status.get_value(
                        name=models.Status.DIRECTION_LOAD_TIME,
                        default=datetime.datetime(2010, 1, 1, 0, 0).isoformat(sep=' ')[:19],
                    )
                    dt_from = iso_to_datetime(dt_from_iso)

                self.load_directions(options, dt_from, dt_to)

                if not origin_dt_from and not origin_dt_to:
                    models.Status.set_value(
                        name=models.Status.DIRECTION_LOAD_TIME,
                        value=dt_to.isoformat(sep=' ')[:19]
                    )

                # если разовый запуск - прекратим
                if not options.get('infinitely'):
                    break

                if options.get('verbosity'):
                    print('Sleep 5 minutes')
                sleep(60 * 5)

                dt_from = dt_to
                dt_to = now()

        except HTTPError as ex:
            # залогируем ошибку в сентри и поспим минуту, чтобы команда не пыталась рестартовать на месте

            logger.critical(
                f'Ошибка загрузки справочников из МИС - {str(ex)[:150]}',
                exc_info=True,
                extra={'action': sw_logger.consts.ACTION_OTHER}
            )
            # в DEBUG режиме, райзим ошибку, чтобы ее отладить
            if settings.DEBUG:
                raise ex

            sleep(60)

    def load_directions(self, options, dt_from, dt_to):
        params = {
            'dm_to': dt_to,
            'dm_from': dt_from
        }

        response = mis.direction.Direction.filter(params)

        for mis_direction in response:
            if options.get('verbosity'):
                print(f'Направление: №{mis_direction.number}')

            worker, created = models.Worker.objects.get_or_create(
                last_name=mis_direction.last_name,
                first_name=mis_direction.first_name,
                birth=mis_direction.birth,
                middle_name=mis_direction.middle_name,
                defaults={
                    'gender': mis_direction.gender
                }
            )
            if not created:
                worker.gender = mis_direction.gender
                worker.save()

            dict_direction = {
                'post': mis_direction.post,
                'shop': mis_direction.shop,
                'exam_type': mis_direction.exam_type,
            }
            if mis_direction.pay_method:
                dict_direction['pay_method'] = mis_direction.pay_method.id
            if mis_direction.insurance_policy:
                dict_direction['insurance_policy'] = mis_direction.insurance_policy.number
            if mis_direction.org:
                dict_direction['org_id'] = mis_direction.org.id

            direction, created = models.Direction.objects.get_or_create(
                worker=worker,
                mis_id=mis_direction.number,
                defaults=dict_direction
            )
            if not created:
                models.Direction.objects\
                    .filter(id=direction.id)\
                    .update(**dict_direction)

            list_law_items_ids = []
            for law_item in mis_direction.law_items:
                obj, _ = models.DirectionLawItem.objects.get_or_create(
                    direction=direction,
                    law_item_mis_id=law_item.id
                )
                list_law_items_ids.append(obj.id)
            models.DirectionLawItem.objects\
                .filter(direction=direction)\
                .exclude(id__in=list_law_items_ids).delete()
