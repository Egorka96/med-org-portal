from rest_framework import serializers
from swutils.date import datetime_to_rus

from background_tasks import models


class Task(serializers.ModelSerializer):
    is_success = serializers.SerializerMethodField()
    is_fail = serializers.SerializerMethodField()
    in_progress = serializers.SerializerMethodField()

    created_dt_rus = serializers.SerializerMethodField()
    start_dt_rus = serializers.SerializerMethodField()
    finish_dt_rus = serializers.SerializerMethodField()

    class Meta:
        model = models.Task
        fields = '__all__'

    def get_is_success(self, obj):
        return obj.is_success()

    def get_is_fail(self, obj):
        return obj.is_fail()

    def get_in_progress(self, obj):
        return obj.in_progress()

    def get_created_dt_rus(self, obj):
        return datetime_to_rus(obj.created_dt)

    def get_start_dt_rus(self, obj):
        return datetime_to_rus(obj.start_dt)

    def get_finish_dt_rus(self, obj):
        return datetime_to_rus(obj.finish_dt)
