from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from katago_server.games.managers.rating_game_pd_manager import RatingGamePdManager
from katago_server.games.models.abstract_game import AbstractGame


class RatingGame(AbstractGame):
    objects = Manager()
    pd = RatingGamePdManager()

    class Meta:
        verbose_name = _("Game: Rating")
        ordering = ['-created_at']
