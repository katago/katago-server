from django.contrib import admin

from katago_server.games.admin.game_admin import GameAdmin
from katago_server.games.models import RatingGame, TrainingGame

admin.site.register(RatingGame, GameAdmin)
admin.site.register(TrainingGame, GameAdmin)
