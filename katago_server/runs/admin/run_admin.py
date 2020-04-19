from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class RunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "name", "status")
    list_filter = ("created_at",)
    readonly_fields = ("id", "created_at", "name", "data_board_len", "inputs_version", "max_search_threads_allowed")
    fieldsets = (
        (None, {"fields": (("id", "created_at", "name"), "status")}),
        ("Config", {"fields": (("data_board_len", "inputs_version", "max_search_threads_allowed"),)}),
    )
