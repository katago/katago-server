from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin

from katago_server.trainings.models import Network, RankingGameGeneratorConfiguration


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "created_at", "size", "log_gamma_upper_confidence", "ranking")
    list_filter = ("created_at", "nb_blocks", "nb_channels")
    readonly_fields = ("id", "created_at", "uuid", "log_gamma_upper_confidence")
    ordering = ("log_gamma_upper_confidence",)
    fieldsets = (
        (None, {
            'fields': (('id', 'uuid', 'created_at'), 'parent_network')
        }),
        (_("Download"), {
            'fields': ('model_file',)
        }),
        (_("Strength"), {
            'fields': (('log_gamma', 'log_gamma_uncertainty'), "log_gamma_upper_confidence")
        }),
        (_("Network architecture"), {
            'fields': (('nb_blocks', 'nb_channels'), 'model_architecture_details')
        }),
    )


admin.site.register(RankingGameGeneratorConfiguration, SingletonModelAdmin)
