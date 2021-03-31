import datetime
from time import sleep

import mis.worker
from django.core.management import BaseCommand
from djutils.management.commands import add_date_from_to_arguments, process_date_from_to_options
from django.utils.timezone import now
import core.models
from swutils.date import iso_to_datetime


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

        while True:
            if not dt_to:
                dt_to = now()
            if not dt_from:
                dt_from_iso = core.models.Status.get_value(
                    name=core.models.Status.WORKER_LOAD_TIME,
                    default=datetime.datetime(2010, 1, 1, 0, 0).isoformat(sep=' ')[:19],
                )
                dt_from = iso_to_datetime(dt_from_iso)

            self.load_workers(options, dt_from, dt_to)

            if not origin_dt_from and not origin_dt_to:
                core.models.Status.set_value(
                    name=core.models.Status.WORKER_LOAD_TIME,
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

    def load_workers(self, options, dt_from, dt_to):
        params = {
            'dm_to': dt_to,
            'dm_from': dt_from
        }

        page = 1
        while True:
            mis_workers = mis.worker.Worker.filter(params)

            for mis_worker in mis_workers:
                worker, created = core.models.Worker.objects.get_or_create(
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
                worker_org, created = core.models.WorkerOrganization.objects.get_or_create(
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
            page += 1

