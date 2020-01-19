from django.contrib import admin

from katago_server.games.admin.game_admin import GameAdmin
from katago_server.games.models import RankingEstimationGame, TrainingGame

admin.site.register(RankingEstimationGame, GameAdmin)
admin.site.register(TrainingGame, GameAdmin)
