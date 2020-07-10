from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from background_tasks import models
from background_tasks import filters
from background_tasks import serializers
from background_tasks import datatools


class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (SessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = models.Task.objects.all()
    filter_class = filters.Task
    serializer_class = serializers.Task

    @action(detail=True, methods=['put'])
    def cancel(self, request, pk):
        task = models.Task.objects.get(id=pk)
        if not request.user.is_superuser and task.user != request.user:
            return Response(status=status.HTTP_404_NOT_FOUND)

        datatools.cancel_task(task)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def restart(self, request, pk):
        task = models.Task.objects.get(id=pk)
        if not request.user.is_superuser and task.user != request.user:
            return Response(status=status.HTTP_404_NOT_FOUND)

        datatools.restart_task(task)
        return Response(status=status.HTTP_200_OK)
