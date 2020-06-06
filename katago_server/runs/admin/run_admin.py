from django.contrib import admin


class RunAdmin(admin.ModelAdmin):
    """
    GameAdmin allows admin to create or edit runs
    """

    list_display = ("id", "created_at", "name", "status")
    list_filter = ("created_at",)
    fieldsets = (
        (None, {"fields": (("id", "created_at", "name"), "status")}),
        (
            "Run parameters",
            {
                "fields": (
                    "data_board_len",
                    "inputs_version",
                    "max_search_threads_allowed",
                    "rating_game_probability",
                    "rating_game_high_elo_probability",
                    "virtual_draw_strength",
                    "elo_number_of_iterations",
                    "selfplay_client_config",
                    "rating_client_config",
                    "git_revision_hash_whitelist",
                )
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        is_editing_existing_run = obj is not None
        if is_editing_existing_run:
            return (
                "id",
                "created_at",
                "name",
                "data_board_len",
                "inputs_version",
                "max_search_threads_allowed",
            )
        else:
            return "id", "created_at"
