from rest_framework import serializers


class WorkerDocuments(serializers.Serializer):
    worker_mis_id = serializers.IntegerField(help_text='ID сотрудника в МИС')
