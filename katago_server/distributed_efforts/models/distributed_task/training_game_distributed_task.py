from django.db.models import ForeignKey, PROTECT
from django.utils.translation import gettext_lazy as _

from katago_server.games.models import TrainingGame

from .abstract_distributed_task import AbstractDistributedTask


class TrainingGameDistributedTask(AbstractDistributedTask):
    class Meta:
        verbose_name = "Task: Training game"

    # The result of a "DONE" RankingGameDistributedTask is a Game
    resulting_game = ForeignKey(TrainingGame, verbose_name=_("resulting training game"), on_delete=PROTECT, null=True, blank=True)
