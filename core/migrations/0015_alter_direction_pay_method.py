# Generated by Django 3.2.5 on 2021-12-20 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20211216_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='direction',
            name='pay_method',
            field=models.IntegerField(blank=True, null=True, verbose_name='Cпособ оплаты'),
        ),
    ]