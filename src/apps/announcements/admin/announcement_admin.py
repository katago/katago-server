from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class AnnouncementAdmin(admin.ModelAdmin):
    """
    AnnouncementAdmin allows admin to create or edit Announcements
    """

    list_display = (
        "id",
        "title",
        "display_order",
        "enabled",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "enabled",
        "display_order",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    ordering = ("display_order",)
    fieldsets = (
        (None, {"fields": (("id", "created_at", "updated_at"),)}),
        (_("Metadata"), {"fields": ("display_order","enabled")},),
        (_("Title"), {"fields": ("title",)},),
        (_("Contents"), {"fields": (("contents"),)},),
        (_("Notes"), {"fields": (("notes"),)},),
    )
