from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class RunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "name", "status")
    list_filter = ("created_at",)
    fieldsets = (
        (None, {"fields": (("id", "created_at", "name"), "status")}),
        ("Run parameters", {"fields": (
            "data_board_len",
            "inputs_version",
            "max_search_threads_allowed",
            "rating_game_probability",
            "rating_game_high_elo_probability",
            "selfplay_client_config",
            "rating_client_config",
        )}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("id", "created_at", "name", "data_board_len", "inputs_version", "max_search_threads_allowed")
        else:
            return ("id", "created_at")
