import os
from enum import Enum

import uuid as uuid
from django.contrib.postgres.fields import JSONField
from django.db.models import Model, CharField, DecimalField, IntegerField, FileField, BooleanField, DateTimeField, \
    ForeignKey, PROTECT, BigAutoField, UUIDField

from katago_server.contrib.validators import FileValidator
from katago_server.games.models import Game
from katago_server.trainings.models import Network
from katago_server.users.models import User


class PredefinedJobStatus(Enum):
    UP_FOR_GRAB = 'up_for_grab'
    ONGOING = 'ongoing'
    DONE = 'done'
    CANCELED = 'canceled'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class PredefinedJobKind(Enum):
    BAYESIAN_ELO_MATCH = 'match'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


def upload_initial_to(instance, filename):
    return os.path.join("initial_position", f"{instance.uuid}.sgf")


validate_sgf = FileValidator(max_size=1024*1024*10, magic_types=("Smart Game Format (Go)",))


class PredefinedJob(Model):
    """
    This class holds a predefined job that will be given in priority to fast client
    """
    # We expect a large number of predefined jobs so lets use BigInt
    id = BigAutoField(primary_key=True)
    uuid = UUIDField(default=uuid.uuid4)
    status = CharField(max_length=15, choices=PredefinedJobStatus.choices(), null=False, default=PredefinedJobStatus.UP_FOR_GRAB)
    # a predefined job has a kind (match), and get attributed to an user with some expiration
    kind = CharField(max_length=15, choices=PredefinedJobKind.choices(), null=False)
    created_at = DateTimeField(auto_now_add=True)
    assigned_to = ForeignKey(User, on_delete=PROTECT, related_name='%(class)s_games')
    assigned_at = DateTimeField(auto_now=True)
    expire_at = DateTimeField()
    # Describe the board/game itself
    board_size_x = IntegerField(null=False, default=19)
    board_size_y = IntegerField(null=False, default=19)
    handicap = IntegerField(null=False, default=0)
    komi = DecimalField(max_digits=3, decimal_places=1, null=False, default=7.0)
    rules_params = JSONField(default=dict, null=True, blank=True)  # See https://lightvector.github.io/KataGo/rules.html
    # The networks related to this game
    white_network = ForeignKey(Network, on_delete=PROTECT, related_name='%(class)s_predefined_jobs_as_white')
    black_network = ForeignKey(Network, on_delete=PROTECT, related_name='%(class)s_predefined_jobs_as_black')
    # A PredefinedJob can be forked from an existing game or a initial situation
    is_forked = BooleanField(default=False)
    forked_initial_position_sgf_file = FileField(null=True, blank=True, upload_to=upload_initial_to, validators=(validate_sgf,))
    forked_at_turn = IntegerField(null=True, blank=True)
    forked_extra_params = JSONField(default=dict, null=True, blank=True)
    # Some extra information about the game like the type
    # eg: komi compensated games, uncompensated games, asymmetric playout games, seki-training games
    game_extra_params = JSONField(default=dict, null=True, blank=True)
    # The result of a "DONE" PredefinedJob is a Game
    result = ForeignKey(Game, on_delete=PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.uuid} ({self.kind})"
