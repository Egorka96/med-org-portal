# Generated by Django 3.0.3 on 2020-03-13 18:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200303_1948'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (('view_workers_done_report', 'Просмотр отчета по прошедшим'), ('view_direction', 'Просмотр направлений на осмотр'), ('add_direction', 'Создание направлений на осмотр'), ('change_direction', 'Редактирование направлений на осмотр'), ('deleter_direction', 'Удаление направлений на осмотр'))},
        ),
    ]
