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
        CREATE TABLE Auth_group (
            id integer,
            name varchar(255),
            modification_time date
        );
        DROP TABLE IF EXISTS Auth_group;
        
        CREATE TABLE Auth_group_permissions (
            id integer,
            group_id integer,
            permission_id integer,
            modification_time date
        );
        DROP TABLE IF EXISTS Auth_group_permissions;
        
        CREATE TABLE Auth_permission (
            id integer,
            name varchar(255),
            content_type_id integer,
            codename varchar(100),
            modification_time date
        );
        DROP TABLE IF EXISTS Auth_permission;
        
        CREATE TABLE Auth_user (
            id integer,
            password varchar(128),
            last_login varchar(255),
            is_superuser boolean,
            username varchar(255),
            first_name varchar(30),
            last_name varchar(150),
            email varchar(254),
            is_staff boolean,
            is_active boolean,
            date_joined date
        );
        DROP TABLE IF EXISTS Auth_user;
        
        CREATE TABLE Auth_user_groups (
            id integer,
            user_id integer,
            group_id integer,
            modification_time date null
        );
        DROP TABLE IF EXISTS Auth_user_groups;
        
        CREATE TABLE Auth_user_user_permissions (
            id integer,
            user_id integer,
            permission_id integer,
            modification_time date null
        );
        DROP TABLE IF EXISTS Auth_user_user_permissions;
        
        CREATE TABLE Authtoken_token (
            key varchar(40),
            created varchar(255),
            user_id integer,
            modification_time date null
        );
        DROP TABLE IF EXISTS Authtoken_token;
        
        CREATE TABLE Background_tasks_task (
            id interval,
            name varchar(255),
            description text,
            user_id integer,
            func_path varchar(255),
            params varchar(100),
            status varchar(255),
            percent varchar(255),
            created_dt varchar(250),
            start_dt varchar(255),
            finich_dt varchar(255),
            result_attachment varchar(255)
        );
        DROP TABLE IF EXISTS Background_tasks_task;
        
        CREATE TABLE Core_directiondocxtemplate (
            id integer,
            name varchar(255),
            description text,
            org_ids varchar(255),
            file varchar(100)
        );
        DROP TABLE IF EXISTS Core_directiondocxtemplate;
        
        CREATE TABLE Core_status (
            id integer,
            name varchar(100),
            value varchar(255)
        );
        DROP TABLE IF EXISTS Core_status;
        
        CREATE TABLE Core_user (
            id integer,
            org_ids varchar(255),
            django_user_id integer,
            post varchar(255),
            modification_time date null
        );
        DROP TABLE IF EXISTS Core_user;
        
        CREATE TABLE Core_useravailabledocumenttype (
            id integer,
            document_type_id integer,
            user_id integer
        );
        DROP TABLE IF EXISTS Core_useravailabledocumenttype;
        
        CREATE TABLE Core_worker(
            id integer,
            birth date,
            first_name varchar(255),
            gender varchar(7),
            last_name varchar(255),
            middle_name varchar(255),
            note text
        );
        DROP TABLE IF EXISTS Core_worker;
        
        CREATE TABLE Core_workerorganization (
            id integer,
            mis_id integer,
            org_id integer,
            post varchar(255),
            shop varchar(255),
            worker_id integer,
            end_work_date date,
            start_work_date date,
            modification_time date null
        );
        DROP TABLE IF EXISTS Core_workerorganization;
        
        CREATE TABLE Django_admin_log (
            action_time date,
            object_id text,
            object_repr varchar(200),
            action_flag varchar(255),
            change_message text,
            content_type_id integer,
            user_id integer
        );
        DROP TABLE IF EXISTS Django_admin_log;
        
        CREATE TABLE Django_content_type (
            id integer,
            app_label varchar(100),
            model varchar(100)
        );
        DROP TABLE IF EXISTS Django_content_type;
        
        CREATE TABLE Django_migrations (
            id integer,
            app varchar(255),
            name varchar(255),
            applied date
        );
        DROP TABLE IF EXISTS Django_migrations;
        
        CREATE TABLE Django_session (
            session_key varchar(40),
            session_data text,
            expire_data date
        )
        DROP TABLE IF EXISTS Django_session;
        '''

        with connection.cursor() as cursor:
            cursor.execute(sql_text)