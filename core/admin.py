from core.models import Worker, WorkersOrganization
from django.contrib import admin

from core import models

admin.site.register(models.DirectionDocxTemplate)


class WorkersOrganizationAdmin(admin.TabularInline):
    model = WorkersOrganization
    fk_name = "worker"
    extra = 0

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    inlines = [
        WorkersOrganizationAdmin,
    ]
