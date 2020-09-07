from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from katago_server.games.managers.rating_game_pandas_manager import RatingGamePandasManager
from katago_server.games.models.abstract_game import AbstractGame


class RatingGame(AbstractGame):
    """
    A rating game involves two different networks and is not used for training but for strength estimation
    """

    objects = Manager()
    pandas = RatingGamePandasManager()

    class Meta:
        verbose_name = _("Rating game")
        ordering = ["-created_at"]

    def clean(self):
        if not self.white_network.rating_games_enabled or not self.black_network.rating_games_enabled:
            raise ValidationError("Network is no longer enabled for rating games")
