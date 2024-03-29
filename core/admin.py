from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User as DjangoUserModel


from core import models


class WorkerOrganizationAdmin(admin.TabularInline):
    model = models.WorkerOrganization
    fk_name = "worker"
    extra = 0


@admin.register(models.Worker)
class WorkerAdmin(admin.ModelAdmin):
    inlines = [WorkerOrganizationAdmin]


class UserInline(admin.TabularInline):
    model = models.User


class ExtendedUser(UserAdmin):
    inlines = UserAdmin.inlines + [UserInline]


admin.site.register(models.DirectionDocxTemplate)
admin.site.register(models.Status)
admin.site.unregister(DjangoUserModel)
admin.site.register(DjangoUserModel, ExtendedUser)


@admin.register(models.Log)
class Log(admin.ModelAdmin):
    search_fields = ('username', 'object_id')
    list_display = ('message', 'created', 'object_name', 'object_id', 'username')
    list_filter = ('created', 'username', 'object_name')
