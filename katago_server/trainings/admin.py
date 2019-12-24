from django.contrib import admin
from katago_server.trainings.models import Network, Gating


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)


@admin.register(Gating)
class GatingAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "modified")
