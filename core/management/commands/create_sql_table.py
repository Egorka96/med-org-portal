from django.core.management import BaseCommand
from djutils.management.commands import add_date_from_to_arguments
from django.db import connection


class Command(BaseCommand):
    args = ''
    help = 'Создание таблицы'

    def add_arguments(self, parser):
        parser.add_argument(
            '--infinitely',
            '-i',
            dest='infinitely',
            action='store_true',
            default=False,
            help='Создание таблицы',
        )
        add_date_from_to_arguments(parser)

    def handle(self, *args, **options):
        sql_text = '''
        CREATE TABLE Background_tasks (
        id int primary key not null,
        task_id int not null,
        description varchar(250) not null,
        ds varchar(250) not null
        );
        DROP TABLE IF EXISTS Background_tasks;
        '''

        with connection.cursor() as cursor:
            cursor.execute(sql_text)