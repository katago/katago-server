from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class RatingGameAdmin(admin.ModelAdmin):
    """
    GameAdmin allows admin to create or edit games
    """

    list_filter = ("run", "created_at", "handicap", "komi")
    list_display = (
        "id",
        "run",
        "created_at",
        "handicap",
        "komi",
        "result_text",
        "submitted_by",
        "white_network",
        "black_network",
    )
    readonly_fields = ("id", "created_at")
    ordering = ("pk",)
    fieldsets = (
        (None, {"fields": (("id", "created_at", "kg_game_uid", "run"),)}),
        (_("Game"), {"fields": (("board_size_x", "board_size_y"), ("handicap", "komi"), "rules",)},),
        (_("Result"), {"fields": (("winner", "score", "resigned"),)}),
        (_("Networks"), {"fields": (("white_network", "black_network"),)}),
        (_("Other"), {"fields": ("submitted_by",)}),
        (_("Download"), {"fields": ("sgf_file",)}),
    )

    def save_model(self, request, obj, form, change):
        is_creating_a_new_game = not obj.pk
        if is_creating_a_new_game:
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)


class TrainingGameAdmin(admin.ModelAdmin):
    """
    GameAdmin allows admin to create or edit games
    """

    list_filter = ("run", "created_at", "handicap", "komi")
    list_display = (
        "id",
        "run",
        "created_at",
        "handicap",
        "komi",
        "result_text",
        "submitted_by",
        "white_network",
        "black_network",
    )
    readonly_fields = ("id", "created_at")
    ordering = ("pk",)
    fieldsets = (
        (None, {"fields": (("id", "created_at", "kg_game_uid", "run"),)}),
        (_("Game"), {"fields": (("board_size_x", "board_size_y"), ("handicap", "komi"), "rules",)},),
        (_("Result"), {"fields": (("winner", "score", "resigned"),)}),
        (_("Networks"), {"fields": (("white_network", "black_network"),)}),
        (_("Other"), {"fields": ("submitted_by",)}),
        (_("Download"), {"fields": (("sgf_file", "training_data_file"),)}),
    )

    def save_model(self, request, obj, form, change):
        is_creating_a_new_game = not obj.pk
        if is_creating_a_new_game:
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)
