from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class StartPosAdmin(admin.ModelAdmin):
    """
    StartPosAdmin allows admin to create or edit StartPoses
    """

    list_display = (
        "id",
        "run",
        "created_at",
        "weight",
    )
    list_filter = (
        "run",
        "created_at",
    )
    readonly_fields = (
        "id",
        "created_at",
        "cumulative_weight",
    )
    ordering = ("created_at",)
    fieldsets = (
        (None, {"fields": (("id", "created_at"), "run")}),
        (_("Weight"), {"fields": (("weight", "cumulative_weight"),)},),
        (_("Data"), {"fields": (("data"),)},),
    )
