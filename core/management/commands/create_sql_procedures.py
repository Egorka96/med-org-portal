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
        sql_text = """
        create procedure worker_insert_procedure(
            id integer,
            birth date,
            first_name varchar(250),
            last_name varchar(250),
            middle_name varchar(250),
            gender varchar(250)
        )
        LANGUAGE SQL
        as $$
            insert into core_worker values (id, birth, first_name, last_name, middle_name, gender);
        $$;
        DROP PROCEDURE IF EXISTS worker_insert_procedure;
        
        create procedure worker_update_procedure(
            id integer,
            birth date,
            first_name varchar(250),
            last_name varchar(250),
            middle_name varchar(250),
            gender varchar(250)
        )
        LANGUAGE SQL
        as $$
            update core_worker
            set birth = birth, first_name = first_name,
                last_name = last_name, middle_name = middle_name, gender = gender
            where id = id
        $$;
        DROP PROCEDURE IF EXISTS worker_update_procedure;
        
        create procedure worker_delete_procedure(
            id integer
        )
        LANGUAGE SQL
        as $$
            delete from core_worker
            where id = id
        $$;
        DROP PROCEDURE IF EXISTS worker_delete_procedure;
        """

        with connection.cursor() as cursor:
            cursor.execute(sql_text)