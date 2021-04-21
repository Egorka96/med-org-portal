# Generated by Django 3.0.7 on 2021-04-06 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20210331_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workerorganization',
            name='shop',
            field=models.CharField(blank=True, max_length=255, verbose_name='Подразделение'),
        ),
        migrations.AlterField(
            model_name='workerorganization',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='worker_orgs', to='core.Worker', verbose_name='Сотрудник'),
        ),
    ]
