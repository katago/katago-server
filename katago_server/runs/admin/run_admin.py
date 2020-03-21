from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class RunAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "name")
    list_filter = ("created_at",)
    readonly_fields = ("id", "created_at")
    fieldsets = (
        (None, {"fields": ("id", "created_at", "name")}),
    )
