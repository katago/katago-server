import os

import uuid as uuid
from django.contrib.postgres.fields import JSONField
from django.db.models import Model, CharField, DecimalField, IntegerField, FileField, BooleanField, DateTimeField, \
    ForeignKey, PROTECT, BigAutoField, UUIDField, DurationField, TextChoices
from django.utils.translation import gettext_lazy as _

from katago_server.contrib.validators import FileValidator
from katago_server.trainings.models import Network
from katago_server.users.models import User

__ALL__ = ["TrainingGame", "RankingEstimationGame"]


def upload_sgf_to(instance, _filename):
    return os.path.join("games", f"{instance.uuid}.sgf")


def upload_unpacked_training_to(instance, _filename):
    return os.path.join("trainings", f"{instance.uuid}.npz")


validate_gzip = FileValidator(max_size=1024*1024*300, content_types=("application/zip",))
validate_sgf = FileValidator(max_size=1024*1024*10, magic_types=("Smart Game Format (Go)",))


class AbstractGame(Model):
    """
    This class holds the common games properties
    """
    class Meta:
        abstract = True

    class GamesResult(TextChoices):
        WHITE = 'W', _("White")
        BLACK = 'B', _("Black")
        DRAW = '0', _("Draw")
        MOSHOUBOU = '-', _("No Result")  # https://senseis.xmp.net/?NoResult

    # We expect a large number of games so lets use BigInt
    id = BigAutoField(primary_key=True)
    uuid = UUIDField(default=uuid.uuid4)
    # A game is submitted by an user
    created_at = DateTimeField(auto_now_add=True)
    submitted_by = ForeignKey(User, on_delete=PROTECT, related_name='%(class)s_games')
    duration = DurationField()
    # Describe the board/game itself
    board_size_x = IntegerField(null=False, default=19)
    board_size_y = IntegerField(null=False, default=19)
    handicap = IntegerField(null=False, default=0)
    komi = DecimalField(max_digits=3, decimal_places=1, null=False, default=7.0)
    rules_params = JSONField(default=dict, null=True, blank=True)  # See https://lightvector.github.io/KataGo/rules.html
    # Some extra information about the game like the type
    # eg: komi compensated games, uncompensated games, asymmetric playout games, seki-training games
    game_extra_params = JSONField(default=dict, null=True, blank=True)
    # The results
    result = CharField(max_length=15, choices=GamesResult.choices, null=False)
    score = DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    has_resigned = BooleanField(default=False)
    # The networks related to this game
    white_network = ForeignKey(Network, on_delete=PROTECT, related_name='%(class)s_games_as_white')
    black_network = ForeignKey(Network, on_delete=PROTECT, related_name='%(class)s_games_as_black')
    # A game can be forked from an existing game or a initial situation
    initial_position_sgf_file = FileField(null=True, blank=True)
    initial_position_extra_params = JSONField(default=dict, null=True, blank=True)
    # The result of the game is stored as an sgf file, always ready to be viewed
    sgf_file = FileField(upload_to=upload_sgf_to, validators=(validate_sgf,))

    @property
    def result_text(self):
        score = "R" if self.has_resigned else self.score
        return f"{self.result}+{score}" if self.result in [AbstractGame.GamesResult.BLACK, AbstractGame.GamesResult.WHITE] else self.result

    def __str__(self):
        return f"{self.uuid} ({self.result_text})"


class TrainingGame(AbstractGame):
    unpacked_file = FileField(upload_to=upload_unpacked_training_to, validators=(validate_gzip,))

    class Meta:
        verbose_name = _("Training Game")


class RankingEstimationGame(AbstractGame):
    class Meta:
        verbose_name = _("Ranking Estimation Game")
