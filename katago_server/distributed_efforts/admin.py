from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from katago_server.distributed_efforts.models import RankingEstimationGameDistributedTask, TrainingGameDistributedTask, DynamicDistributedTaskConfiguration


@admin.register(RankingEstimationGameDistributedTask)
@admin.register(TrainingGameDistributedTask)
class GameDistributedTaskAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'created_at', 'assigned_to', 'assigned_at', 'expire_at', 'white_network', 'black_network')
    list_filter = ("created_at", "assigned_at", 'expire_at')
    readonly_fields = ("id", "created_at", "uuid")
    ordering = ("pk",)
    fieldsets = (
        (None, {
            'fields': (('id', 'uuid', 'created_at'),)
        }),
        (_("Network"), {
            'fields': (('white_network', 'black_network'),)
        }),
    )


admin.site.register(DynamicDistributedTaskConfiguration, SingletonModelAdmin)
