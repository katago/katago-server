from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class GameDistributedTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "run", "status", "created_at", "assigned_to", "assigned_at", "expire_at", "white_network", "black_network")
    list_filter = ("run", "created_at", "status", "assigned_at", "expire_at")
    readonly_fields = ("id", "created_at")
    ordering = ("pk",)
    fieldsets = (
        (None, {"fields": (("id", "uuid", "created_at", "run"),)}),
        (_("Network"), {"fields": (("white_network", "black_network"),)}),
    )
