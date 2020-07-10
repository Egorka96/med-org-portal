from django.contrib import admin
from background_tasks import models


class LogInline(admin.TabularInline):
    model = models.Log
    extra = 0


class Task(admin.ModelAdmin):
    inlines = (LogInline, )
    list_display = ('name', 'user', 'func_path', 'params', 'status', 'percent',
                    'created_dt', 'start_dt', 'finish_dt')
    list_filter = ('name', 'func_path', 'status', 'user')


admin.site.register(models.Task, Task)
