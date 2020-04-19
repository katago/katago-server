import random

from django.db.models import ForeignKey, PROTECT
from django.utils.translation import gettext_lazy as _

from katago_server.games.models import RankingEstimationGame

from .abstract_distributed_task import AbstractDistributedTask


class RankingEstimationGameDistributedTask(AbstractDistributedTask):
    class Meta:
        verbose_name = "Task: Ranking estimation game"

    # The result of a "DONE" RankingGameDistributedTask is a Game
    resulting_game = ForeignKey(RankingEstimationGame, verbose_name=_("resulting ranking game"), on_delete=PROTECT, null=True, blank=True)

    @classmethod
    def create_with_random_color(cls, run, reference_network, opponent_network):
        """
        Given two network, create a ranking game task.
        Half of the time, first network will play white, half black.

        :param reference_network: First network
        :param opponent_network: Second network
        :return:
        """
        if random.random() < 0.5:
            return cls(run=run, white_network=reference_network, black_network=opponent_network)
        else:
            return cls(run=run, white_network=opponent_network, black_network=reference_network)
