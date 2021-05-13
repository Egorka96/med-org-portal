from django.core.management import BaseCommand
from djutils.management.commands import add_date_from_to_arguments
from django.db import connection


class Command(BaseCommand):
    args = ''
    help = 'Создание представления'

    def add_arguments(self, parser):
        parser.add_argument(
            '--infinitely',
            '-i',
            dest='infinitely',
            action='store_true',
            default=False,
            help='Создание представления',
        )
        add_date_from_to_arguments(parser)

    def handle(self, *args, **options):
        sql_text = '''
        CREATE VIEW worker_list
        AS
        select cw.last_name, cw.first_name, cw.middle_name, cw.gender, cw.birth,
        age(CURRENT_TIMESTAMP , cw.birth) as age,
        cwo.mis_id, cwo.org_id, cwo.post, cwo.shop from core_worker cw
        inner join core_workerorganization cwo on cw.id = cwo.worker_id;
        DROP VIEW IF EXISTS worker_list;
        
        CREATE VIEW user_list
        AS
        select cw.last_name, cw.first_name, cw.middle_name, c.post from core_worker cw
        inner join core_workerorganization c on cw.id = c.worker_id;
        DROP VIEW IF EXISTS user_list;
        
        CREATE VIEW background_task
        AS
        select description, name, status, percent, created_dt,  concat(start_dt, ' - ', finish_dt) as duration
        from background_tasks_task;
        DROP VIEW IF EXISTS background_task;
        '''

        with connection.cursor() as cursor:
            cursor.execute(sql_text)
