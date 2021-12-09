# Generated by Django 3.2 on 2021-12-08 00:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sw_logger', '0005_add_indexes'),
        ('core', '0010_auto_20210813_1735'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('log_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sw_logger.log')),
            ],
            options={
                'verbose_name': 'Запись в журнале',
                'verbose_name_plural': 'Журнал',
                'ordering': ('id',),
            },
            bases=('sw_logger.log',),
        ),
        migrations.AlterModelOptions(
            name='workerorganization',
            options={'verbose_name': 'Сотрудник организации', 'verbose_name_plural': 'Сотрудники организации'},
        ),
    ]
