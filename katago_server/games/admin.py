from django.contrib import admin
from katago_server.games.models import SelfPlay, Match, ForkedGame


@admin.register(SelfPlay)
class SelfPlayAdmin(admin.ModelAdmin):
    pass


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    pass


@admin.register(ForkedGame)
class ForkedGameAdmin(admin.ModelAdmin):
    pass
