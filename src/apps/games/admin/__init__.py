from django.contrib import admin

from src.apps.games.admin.game_admin import RatingGameAdmin, TrainingGameAdmin
from src.apps.games.models import RatingGame, TrainingGame

admin.site.register(RatingGame, RatingGameAdmin)
admin.site.register(TrainingGame, TrainingGameAdmin)
