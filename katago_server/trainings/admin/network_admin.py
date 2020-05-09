from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class NetworkAdmin(admin.ModelAdmin):
    """
    NetworkAdmin allows admin to create or edit networks
    """
    list_display = ("id", "run", "name", "created_at", "size", "log_gamma_upper_confidence", "log_gamma_lower_confidence", "rating")
    list_filter = ("run", "created_at", "network_size")
    readonly_fields = ("id", "created_at", "log_gamma", "log_gamma_uncertainty", "log_gamma_upper_confidence", "log_gamma_lower_confidence")
    ordering = ("log_gamma_upper_confidence",)
    fieldsets = (
        (None, {"fields": (("id", "created_at"), ("name", "run"), "parent_network")}),
        (_("Model File"), {"fields": (("model_file", "model_file_bytes", "model_file_sha256"),)}),
        (_("Strength"), {"fields": (("log_gamma", "log_gamma_uncertainty"), "log_gamma_upper_confidence")}),
        (_("Network architecture"), {"fields": (''"network_size", "is_random"),}),
    )

