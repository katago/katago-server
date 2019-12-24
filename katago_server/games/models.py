from enum import Enum

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db.models import Model, CharField, DecimalField, IntegerField, FileField, BooleanField, DateTimeField, \
    ForeignKey, PROTECT

from katago_server.trainings.models import Gating, Network


class KoRulesType(Enum):
    SIMPLE = 'Simple'
    POSITIONAL = 'Positional'
    SITUATIONAL = 'Situational'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class ScoringRulesType(Enum):
    AREA = 'Area'
    TERRITORY = 'Territory'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class TaxRulesType(Enum):
    NONE = 'None'
    SEKI = 'Seki'
    ALL = 'All'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class GamesResultType(Enum):
    WHITE = 'W'
    BLACK = 'B'
    JIGO = '0'
    MOSHOUBOU = '∅'  # https://senseis.xmp.net/?NoResult

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Game(Model):
    """
    This abstract class holds the games property that are common, no matter if the game is a self play, a branched game,
    a match or an human game.
    """
    board_size = ArrayField(IntegerField(null=False, default=19), size=2)
    handicap = IntegerField(null=False, default=0)
    komi = DecimalField(max_digits=3, decimal_places=1, null=False, default=7.0)

    ko_rule = CharField(max_length=15, choices=KoRulesType.choices(), null=False)
    scoring_rule = CharField(max_length=15, choices=ScoringRulesType.choices(), null=False)
    tax_rule = CharField(max_length=15, choices=TaxRulesType.choices(), null=False)
    multi_stone_suicide_allowed = BooleanField()
    extra_rules = JSONField()

    result = CharField(max_length=15, choices=GamesResultType.choices(), null=False)
    has_resigned = BooleanField()
    score = DecimalField(max_digits=4, decimal_places=1)

    created = DateTimeField(auto_now_add=True)

    sgf_file = FileField()

    class Meta:
        abstract = True


class Match(Game):
    gating = ForeignKey(Gating, on_delete=PROTECT)

    class Meta:
        verbose_name_plural = 'Matches'


class SelfPlay(Game):
    network = ForeignKey(Network, on_delete=PROTECT)

    unpacked_training_file = FileField()
    packed_training_file = FileField()

    game_extra_params = JSONField()


class ForkedSelfPlay(Game):
    network = ForeignKey(Network, on_delete=PROTECT)

    unpacked_training_file = FileField()
    packed_training_file = FileField()

    parent_sgf_file = FileField()
    forked_at_turn = IntegerField()

    game_extra_params = JSONField()
