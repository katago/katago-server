from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from katago_server.distributed_efforts.models import RankingEstimationGameDistributedTask, TrainingGameDistributedTask, DynamicDistributedTaskConfiguration


@admin.register(RankingEstimationGameDistributedTask)
@admin.register(TrainingGameDistributedTask)
class GameDistributedTaskAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'created_at', 'assigned_to', 'assigned_at', 'expire_at', 'komi', 'handicap', 'white_network', 'black_network')
    list_filter = ("created_at", "assigned_at", 'expire_at', "handicap", "komi")
    readonly_fields = ("id", "created_at", "uuid")
    ordering = ("pk",)
    fieldsets = (
        (None, {
            'fields': (('id', 'uuid', 'created_at'),)
        }),
        (_("Game"), {
            'fields': (('board_size_x', 'board_size_y'), ('handicap', 'komi'), 'rules_params')
        }),
        (_("Network"), {
            'fields': (('white_network', 'black_network'),)
        }),
    )


    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set added_by during the first save.
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(DynamicDistributedTaskConfiguration, SingletonModelAdmin)
