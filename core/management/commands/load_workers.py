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

import mis.worker
from core import models

logger = logging.getLogger('db')


class Command(BaseCommand):
    args = ''
    help = 'Выгрузка сотрудников из мис'

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
                        name=models.Status.WORKER_LOAD_TIME,
                        default=datetime.datetime(2010, 1, 1, 0, 0).isoformat(sep=' ')[:19],
                    )
                    dt_from = iso_to_datetime(dt_from_iso)

                self.load_workers(options, dt_from, dt_to)

                if not origin_dt_from and not origin_dt_to:
                    models.Status.set_value(
                        name=models.Status.WORKER_LOAD_TIME,
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

    def load_workers(self, options, dt_from, dt_to):
        params = {
            'dm_to': dt_to,
            'dm_from': dt_from
        }

        page = 1
        while True:
            params['page'] = page
            response = mis.worker.Worker.filter_with_response(params)

            for mis_worker in response['results']:
                if options.get('verbosity'):
                    print(mis_worker)
                worker, created = models.Worker.objects.get_or_create(
                    last_name=mis_worker.last_name,
                    first_name=mis_worker.first_name,
                    birth=mis_worker.birth,
                    middle_name=mis_worker.middle_name,
                    defaults={
                        'gender': mis_worker.gender
                    }
                )
                if not created:
                    worker.gender = mis_worker.gender
                    worker.save()
                worker_org, created = models.WorkerOrganization.objects.get_or_create(
                    worker=worker,
                    org_id=mis_worker.org.id,
                    mis_id=mis_worker.id,
                    defaults={
                        'post': mis_worker.post,
                        'shop': mis_worker.shop
                    }
                )
                if not created:
                    worker_org.post = mis_worker.post
                    worker_org.shop = mis_worker.shop
                    worker_org.save()
                worker_org.save()

            if not response.get('next'):
                break
            page += 1
