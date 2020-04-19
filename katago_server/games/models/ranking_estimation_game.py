from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from katago_server.games.managers.ranking_estimation_game_pd_manager import RankingEstimationGamePdManager
from katago_server.games.models.abstract_game import AbstractGame


class RankingEstimationGame(AbstractGame):
    objects = Manager()
    pd = RankingEstimationGamePdManager()

    class Meta:
        verbose_name = _("Game: Ranking Estimation")
        ordering = ['-created_at']
