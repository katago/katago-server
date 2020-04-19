from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class NetworkAdmin(admin.ModelAdmin):
    list_display = ("id", "run", "name", "created_at", "size", "log_gamma_upper_confidence", "log_gamma_lower_confidence", "ranking")
    list_filter = ("run", "created_at", "network_size", "nb_parameters")
    readonly_fields = ("id", "created_at", "name", "log_gamma_upper_confidence", "log_gamma_lower_confidence")
    ordering = ("log_gamma_upper_confidence",)
    fieldsets = (
        (None, {"fields": (("id", "name", "created_at", "run"), "parent_network")}),
        (_("Download"), {"fields": ("model_file",)}),
        (_("Strength"), {"fields": (("log_gamma", "log_gamma_uncertainty"), "log_gamma_upper_confidence")}),
        (_("Network architecture"), {"fields": (("network_size", "nb_parameters"), "model_architecture_details")}),
    )

