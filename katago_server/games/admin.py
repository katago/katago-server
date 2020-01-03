from django.contrib import admin
from katago_server.games.models import TrainingGame, RankingEstimationGame


@admin.register(TrainingGame)
class TrainingGameAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)
    list_display = ('uuid', 'result_text', 'created_at', 'submitted_by', 'white_network', 'black_network')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set added_by during the first save.
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(RankingEstimationGame)
class RankingEstimationGameAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)
    list_display = ('uuid', 'result_text', 'created_at', 'submitted_by', 'white_network', 'black_network')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set added_by during the first save.
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)
