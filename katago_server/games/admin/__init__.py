from django.contrib import admin

from katago_server.games.admin.game_admin import RatingGameAdmin, TrainingGameAdmin
from katago_server.games.models import RatingGame, TrainingGame

admin.site.register(RatingGame, RatingGameAdmin)
admin.site.register(TrainingGame, TrainingGameAdmin)
