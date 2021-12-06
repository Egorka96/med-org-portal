from rest_framework import serializers

from core import models


class Documents(serializers.Serializer):
    search_params = serializers.CharField(help_text='поисковый запрос типа "prof=1&heal=2"')


class WorkerDocuments(serializers.Serializer):
    worker = serializers.PrimaryKeyRelatedField(queryset=models.Worker.objects.all())


class DocumentPrint(serializers.Serializer):
    name = serializers.CharField(help_text='название, которое нужно дать файлу')
    link = serializers.CharField(help_text='ссылка на скачивание документа в МИС')
