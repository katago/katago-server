from django.contrib import admin
from katago_server.games.models import SelfPlay, Match, ForkedSelfPlay


@admin.register(SelfPlay)
class SelfPlayAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)


@admin.register(ForkedSelfPlay)
class ForkedSelfPlayAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)
