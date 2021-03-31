from django.contrib import admin

from core import models

admin.site.register(models.DirectionDocxTemplate)
admin.site.register(models.Status)


class WorkerOrganizationAdmin(admin.TabularInline):
    model = models.WorkerOrganization
    fk_name = "worker"
    extra = 0


@admin.register(models.Worker)
class WorkerAdmin(admin.ModelAdmin):
    inlines = [WorkerOrganizationAdmin]
