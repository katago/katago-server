from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class NetworkAdmin(admin.ModelAdmin):
    """
    NetworkAdmin allows admin to create or edit networks
    """

    list_display = (
        "id",
        "run",
        "name",
        "created_at",
        "size",
        "log_gamma",
        "log_gamma_uncertainty",
        "rating",
        "training_games_enabled",
        "rating_games_enabled",
    )
    list_filter = (
        "run",
        "created_at",
        "network_size",
        "training_games_enabled",
        "rating_games_enabled",
    )
    readonly_fields = (
        "id",
        "created_at",
        "log_gamma",
        "log_gamma_uncertainty",
        "log_gamma_upper_confidence",
        "log_gamma_lower_confidence",
        "log_gamma_game_count",
    )
    ordering = ("created_at",)
    fieldsets = (
        (None, {"fields": (("id", "created_at"), ("name", "run"), "parent_network")}),
        (
            _("Model File"),
            {"fields": (("model_file", "model_file_bytes", "model_file_sha256"),)},
        ),
        (
            _("Model Zip Extras"),
            {"fields": (("model_zip_file"),)},
        ),
        (
            _("Strength"),
            {
                "fields": (
                    (
                        "log_gamma",
                        "log_gamma_uncertainty",
                        "log_gamma_game_count",
                    ),
                    ("log_gamma_lower_confidence", "log_gamma_upper_confidence"),
                )
            },
        ),
        (_("Network architecture"), {"fields": (("network_size", "is_random"),)}),
        (_("Stats"), {"fields": (("train_step", "total_num_data_rows", "extra_stats"),)}),
        (_("Enable/Disable"), {"fields": (("training_games_enabled", "rating_games_enabled"),)}),
        (
            _("Notes"),
            {"fields": (("notes"),)},
        ),
    )
