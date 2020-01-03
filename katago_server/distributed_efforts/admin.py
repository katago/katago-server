from django.contrib import admin
from solo.admin import SingletonModelAdmin

from katago_server.distributed_efforts.models import RankingEstimationGameDistributedTask, TrainingGameDistributedTask, DynamicDistributedTaskConfiguration


@admin.register(RankingEstimationGameDistributedTask)
class RankingEstimationGameDistributedTaskAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)
    list_display = ('uuid', 'created_at', 'assigned_to', 'assigned_at', 'expire_at', 'white_network', 'black_network')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set added_by during the first save.
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TrainingGameDistributedTask)
class TrainingGameDistributedTaskAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)
    list_display = ('uuid', 'created_at', 'assigned_to', 'assigned_at', 'expire_at', 'white_network', 'black_network')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set added_by during the first save.
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(DynamicDistributedTaskConfiguration, SingletonModelAdmin)
