from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from katago_server.trainings.models import Network


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "created_at", "size", "ranking")
    list_filter = ("created_at", "nb_blocks", "nb_channels")
    readonly_fields = ("id", "created_at", "uuid")
    ordering = ("pk",)
    fieldsets = (
        (None, {
            'fields': (('id', 'uuid', 'created_at'),)
        }),
        (_("Download"), {
            'fields': ('model_file',)
        }),
        (_("Strength"), {
            'fields': (('log_gamma', 'log_gamma_uncertainty'),)
        }),
        (_("Network architecture"), {
            'fields': (('nb_blocks', 'nb_channels'), 'model_architecture_details')
        }),
    )
