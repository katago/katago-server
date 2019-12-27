import os
from enum import Enum

import uuid as uuid
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db.models import Model, CharField, DecimalField, IntegerField, FileField, BooleanField, DateTimeField, \
    ForeignKey, PROTECT, BigAutoField, UUIDField, DurationField

from katago_server.trainings.models import Network
from katago_server.users.models import User


class GamesResultType(Enum):
    WHITE = 'W'
    BLACK = 'B'
    JIGO = '0'
    MOSHOUBOU = '∅'  # https://senseis.xmp.net/?NoResult

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


def upload_sgf_to(instance, filename):
    return os.path.join("games", f"{instance.uuid}.sgf")


def upload_unpacked_training_to(instance, filename):
    return os.path.join("trainings", f"{instance.uuid}.gz")


class Game(Model):
    """
    This class holds the games properties, no matter if it is a self play, a branched game, a match or an human game.
    """
    # We expect a large number of games so lets use BigInt
    id = BigAutoField(primary_key=True)
    uuid = UUIDField(default=uuid.uuid4)
    # A game is submitted by an user
    created_at = DateTimeField(auto_now_add=True)
    submitted_by = ForeignKey(User, on_delete=PROTECT, related_name='%(class)s_games')
    duration = DurationField()
    # Describe the board/game itself
    board_size = ArrayField(IntegerField(null=False, default=19), size=2)  # A [X, Y] array of integers
    handicap = IntegerField(null=False, default=0)
    komi = DecimalField(max_digits=3, decimal_places=1, null=False, default=7.0)
    rules_params = JSONField(default=dict, null=True, blank=True)  # See https://lightvector.github.io/KataGo/rules.html
    # The results
    result = CharField(max_length=15, choices=GamesResultType.choices(), null=False)
    has_resigned = BooleanField()
    score = DecimalField(max_digits=4, decimal_places=1)
    # The networks related to this game
    white_network = ForeignKey(Network, on_delete=PROTECT, related_name='%(class)s_games_as_white')
    black_network = ForeignKey(Network, on_delete=PROTECT, related_name='%(class)s_gates_as_black')
    # A game can be forked from an existing game or a initial situation
    is_forked = BooleanField(default=False)
    forked_initial_position_sgf_file = FileField(null=True, blank=True)
    forked_at_turn = IntegerField(null=True, blank=True)
    forked_extra_params = JSONField(default=dict, null=True, blank=True)
    # Some extra information about the game like the type
    # eg: komi compensated games, uncompensated games, asymmetric playout games, seki-training games
    game_extra_params = JSONField(default=dict, null=True, blank=True)
    # The result of the game is stored as an sgf file, always ready to be viewed, and some training data
    sgf_file = FileField(upload_to=upload_sgf_to)
    unpacked_file = FileField(upload_to=upload_unpacked_training_to)

    @property
    def result_text(self):
        score = "R" if self.has_resigned else self.score
        return f"{self.result}+{score}" if self.result in [GamesResultType.BLACK, GamesResultType.WHITE] \
            else self.result

    def __str__(self):
        return f"{self.uuid} ({self.result_text})"
