import subprocess

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Создание backup'

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--file",
            dest='file',
            type=str,
            help='Восстановление backup БД',
        )

    def handle(self, *args, **options):
        path = options["file"] if options["file"] else 21
        subprocess.call(f"$ pg_restore -d portal {path}/db.dump", shell=True)