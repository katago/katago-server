from enum import Enum

from django.db.models import Model, CharField, DecimalField, IntegerField


class GamesRulesType(Enum):
    JAPANESE = 'Japanese'
    CHINESE = 'Chinese'
    TROMP_TAYLOR = 'Trump Taylor'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class GamesResultType(Enum):
    WHITE = 'W'
    BLACK = 'B'
    JIGO = '0'
    # https://senseis.xmp.net /?NoResult
    MOSHOUBOU = '∅'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Games(Model):
    """
    This abstract class holds the games property that are common, no matter if the game is a self play, a branched game,
    a match or an human game.
    """
    rules = CharField(max_length=20, choices=GamesRulesType.choices(), null=False, default=GamesRulesType.CHINESE)
    handicap = IntegerField(null=False, default=0)
    komi = DecimalField(max_digits=3, decimal_places=1, null=False, default=7.0)
    result = CharField(max_length=15, choices=GamesResultType.choices(), null=False)
    score = DecimalField(max_digits=4, decimal_places=1)

    class Meta:
        abstract = True


class SelfPlay(Games):
    pass


class Match(Games):
    class Meta:
        verbose_name_plural = 'Matches'
