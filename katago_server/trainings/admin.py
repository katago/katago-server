from django.contrib import admin
from katago_server.trainings.models import Network


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)
