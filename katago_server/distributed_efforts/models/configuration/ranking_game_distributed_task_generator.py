from random import random

from django.db.models import FloatField
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel


class RankingGameDistributedTaskGeneratorConfiguration(SingletonModel):
    class Meta:
        verbose_name = "Configuration: Parameters to schedule ranking matches"

    probability_high_elo = FloatField(
        _("ranking game probability of being high elo game"),
        help_text=_("Ranking (matches) games are high_elo game or big uncertainty game"),
        default=0.4,
    )
    ratio = FloatField(_("ranking game ration"), help_text=_("eg 0.1 means that for 10 of training games, there will be 1 match game"), default=0.1)

    def __str__(self):
        return "Configuration: Parameters to schedule ranking matches"

    def should_play_high_elo(self):
        return random.random() < self.probability_high_elo
