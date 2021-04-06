from rest_framework import serializers

from core import models


class WorkerDocuments(serializers.Serializer):
    worker = serializers.PrimaryKeyRelatedField(queryset=models.Worker.objects.all())
