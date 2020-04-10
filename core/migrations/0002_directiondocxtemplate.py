# Generated by Django 3.0.3 on 2020-03-18 22:38

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectionDocxTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('org_ids', models.CharField(blank=True, help_text='список id организаций из внешней системы', max_length=255, verbose_name='Список ID организаций')),
                ('file', models.FileField(upload_to='core/direction_docx_templates/', validators=[core.models.docx_file_extension], verbose_name='Файл шаблона')),
            ],
            options={
                'verbose_name': 'Шаблон направления на осмотр',
                'verbose_name_plural': 'Шаблоны направлений на осмотр',
                'ordering': ('name',),
            },
        ),
    ]