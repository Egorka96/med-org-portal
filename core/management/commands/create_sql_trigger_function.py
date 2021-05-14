from django.core.management import BaseCommand
from djutils.management.commands import add_date_from_to_arguments
from django.db import connection


class Command(BaseCommand):
    args = ''
    help = 'Создание поля modification_time'

    def add_arguments(self, parser):
        parser.add_argument(
            '--infinitely',
            '-i',
            dest='infinitely',
            action='store_true',
            default=False,
            help='Создание поля modification_time',
        )
        add_date_from_to_arguments(parser)

    def handle(self, *args, **options):
        sql_text = '''
        CREATE OR REPLACE FUNCTION worker_modification_time() RETURNS trigger AS $worker_modification_time$
            BEGIN
                NEW.modification_time := current_timestamp;
                RETURN NEW;
            END;
        $worker_modification_time$ LANGUAGE plpgsql;
        
        CREATE TRIGGER worker_modification_time BEFORE INSERT OR UPDATE ON core_worker
            FOR EACH ROW EXECUTE PROCEDURE worker_modification_time();
        
        DROP TRIGGER  IF EXISTS  worker_modification_time ON core_worker;
        DROP FUNCTION IF EXISTS worker_modification_time();
        
        CREATE OR REPLACE FUNCTION core_workerorganization_modification_time() RETURNS trigger AS $core_workerorganization_modification_time$
            BEGIN
                NEW.modification_time := current_timestamp;
                RETURN NEW;
            END;
        $core_workerorganization_modification_time$ LANGUAGE plpgsql;
        
        CREATE TRIGGER core_workerorganization_modification_time BEFORE INSERT OR UPDATE ON core_workerorganization
            FOR EACH ROW EXECUTE PROCEDURE core_workerorganization_modification_time();
        
        DROP TRIGGER  IF EXISTS  core_workerorganization_modification_time ON core_workerorganization;
        DROP FUNCTION IF EXISTS worker_modification_time();
        
        CREATE OR REPLACE FUNCTION auth_group_modification_time() RETURNS trigger AS $auth_group_modification_time$
            BEGIN
                NEW.modification_time := current_timestamp;
                RETURN NEW;
            END;
        $auth_group_modification_time$ LANGUAGE plpgsql;
        
        CREATE TRIGGER auth_group_modification_time BEFORE INSERT OR UPDATE ON auth_group
            FOR EACH ROW EXECUTE PROCEDURE auth_group_modification_time();
        
        DROP TRIGGER  IF EXISTS  auth_group_modification_time ON auth_group;
        DROP FUNCTION IF EXISTS auth_group_modification_time();
        
        CREATE OR REPLACE FUNCTION auth_group_permissions_modification_time() RETURNS trigger AS $auth_group_permissions_modification_time$
            BEGIN
                NEW.modification_time := current_timestamp;
                RETURN NEW;
            END;
        $auth_group_permissions_modification_time$ LANGUAGE plpgsql;
        
        CREATE TRIGGER auth_group_permissions_modification_time BEFORE INSERT OR UPDATE ON auth_group_permissions
            FOR EACH ROW EXECUTE PROCEDURE auth_group_permissions_modification_time();
        
        DROP TRIGGER  IF EXISTS  auth_group_permissions_modification_time ON auth_group_permissions;
        DROP FUNCTION IF EXISTS auth_group_permissions_modification_time();
        
        CREATE OR REPLACE FUNCTION auth_permission_modification_time() RETURNS trigger AS $auth_permission_modification_time$
            BEGIN
                NEW.modification_time := current_timestamp;
                RETURN NEW;
            END;
        $auth_permission_modification_time$ LANGUAGE plpgsql;
        
        CREATE TRIGGER auth_permission_modification_time BEFORE INSERT OR UPDATE ON auth_permission
            FOR EACH ROW EXECUTE PROCEDURE auth_permission_modification_time();
        
        DROP TRIGGER  IF EXISTS  auth_permission_modification_time ON auth_permission;
        DROP FUNCTION IF EXISTS auth_permission_modification_time();
        
        CREATE OR REPLACE FUNCTION auth_user_modification_time() RETURNS trigger AS $auth_user_modification_time$
            BEGIN
                NEW.modification_time := current_timestamp;
                RETURN NEW;
            END;
        $auth_user_modification_time$ LANGUAGE plpgsql;
        
        CREATE TRIGGER auth_user_modification_time BEFORE INSERT OR UPDATE ON auth_user
            FOR EACH ROW EXECUTE PROCEDURE auth_user_modification_time();
        
        DROP TRIGGER  IF EXISTS  auth_user_modification_time ON auth_user;
        DROP FUNCTION IF EXISTS auth_user_modification_time();
        
        CREATE OR REPLACE FUNCTION auth_user_groups_modification_time() RETURNS trigger AS $auth_user_groups_modification_time$
            BEGIN
                NEW.modification_time := current_timestamp;
                RETURN NEW;
            END;
        $auth_user_groups_modification_time$ LANGUAGE plpgsql;
        
        CREATE TRIGGER auth_user_groups_modification_time BEFORE INSERT OR UPDATE ON auth_user_groups
            FOR EACH ROW EXECUTE PROCEDURE auth_user_groups_modification_time();
        
        DROP TRIGGER  IF EXISTS  auth_user_groups_modification_time ON auth_user_groups;
        DROP FUNCTION IF EXISTS auth_user_groups_modification_time();
        
        CREATE OR REPLACE FUNCTION auth_user_user_permissions_modification_time() RETURNS trigger AS $auth_user_user_permissions_modification_time$
            BEGIN
                NEW.modification_time := current_timestamp;
                RETURN NEW;
            END;
        $auth_user_user_permissions_modification_time$ LANGUAGE plpgsql;
        
        CREATE TRIGGER auth_user_user_permissions_modification_time BEFORE INSERT OR UPDATE ON auth_user_user_permissions
            FOR EACH ROW EXECUTE PROCEDURE auth_user_user_permissions_modification_time();
        
        DROP TRIGGER  IF EXISTS  auth_user_user_permissions_modification_time ON auth_user_user_permissions;
        DROP FUNCTION IF EXISTS auth_user_user_permissions_modification_time();
        
        CREATE OR REPLACE FUNCTION authtoken_token_modification_time() RETURNS trigger AS $authtoken_token_modification_time$
            BEGIN
                NEW.modification_time := current_timestamp;
                RETURN NEW;
            END;
        $authtoken_token_modification_time$ LANGUAGE plpgsql;
        
        CREATE TRIGGER authtoken_token_modification_time BEFORE INSERT OR UPDATE ON authtoken_token
            FOR EACH ROW EXECUTE PROCEDURE authtoken_token_modification_time();
        
        DROP TRIGGER  IF EXISTS  authtoken_token_modification_time ON authtoken_token;
        DROP FUNCTION IF EXISTS authtoken_token_modification_time();
        
        CREATE OR REPLACE FUNCTION core_user_modification_time() RETURNS trigger AS $core_user_modification_time$
            BEGIN
                NEW.modification_time := current_timestamp;
                RETURN NEW;
            END;
        $core_user_modification_time$ LANGUAGE plpgsql;
        
        CREATE TRIGGER core_user_modification_time BEFORE INSERT OR UPDATE ON core_user
            FOR EACH ROW EXECUTE PROCEDURE core_user_modification_time();
        
        DROP TRIGGER  IF EXISTS  core_user_modification_time ON core_user;
        DROP FUNCTION IF EXISTS core_user_modification_time();
        '''

        with connection.cursor() as cursor:
            cursor.execute(sql_text)