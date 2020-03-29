import random

from django.db.models import TextField, FloatField
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel


class DynamicDistributedTaskConfiguration(SingletonModel):
    def __str__(self):
        return "Configuration: Katago config"

    class Meta:
        verbose_name = "Configuration: Katago config"

    katago_config = TextField(
        _("katago config"), help_text=_("The configuration file for katago to be given to client for selfplay"), default="FILL ME"
    )
    # QUESTION (lightvector): I assume "probability_predefined_training_game" is supposed to be the games that start from specified SGF positions?
    # If this is correct, why is there the word "predefined" in "probability_predefined_ranking_game"? Shouldn't it just be "probability_ranking_game"?
    # Also, how does this interact with "ratio" in ranking_game_distributed_task_generator.py?
    probability_predefined_ranking_game = FloatField(
        _("probability of playing ranking game"),
        help_text=_("If random() < probability, it will play ranking game (if any), else will play either predefined game, or dynamic one"),
        default=0.5,
    )
    probability_predefined_training_game = FloatField(
        _("probability of playing predefined game"),
        help_text=_("If random() < probability, it will play predefined game (if any), else will play dynamic one"),
        default=0.25,
    )

    def should_play_predefined_ranking_game(self):
        return random.random() < self.probability_predefined_ranking_game

    def should_play_predefined_training_game(self):
        return random.random() < self.probability_predefined_training_game
