# Generated by Django 3.2.5 on 2022-03-01 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_merge_0011_auto_20211206_1806_0011_auto_20211208_0055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='org_ids',
            field=models.TextField(help_text='список id организаций из внешней системы', verbose_name='ID организаций'),
        ),
    ]
