from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class GameAdmin(admin.ModelAdmin):
    list_filter = ("run", "created_at", "handicap", "komi")
    list_display = ("id", "run", "created_at", "handicap", "komi", "result_text", "submitted_by", "white_network", "black_network")
    readonly_fields = ("id", "created_at")
    ordering = ("pk",)
    fieldsets = (
        (None, {"fields": (("id", "created_at", "kg_game_uid", "run"),)}),
        (_("Game"), {"fields": (("board_size_x", "board_size_y"), ("handicap", "komi"), "rules")}),
        (_("Result"), {"fields": (("winner", "score", "has_resigned"),)}),
        (_("Networks"), {"fields": (("white_network", "black_network"),)}),
        (_("Other"), {"fields": ("submitted_by",)}),
        (_("Download"), {"fields": ("sgf_file",)}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set added_by during the first save.
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)
