import os

import uuid as uuid
from django.contrib.postgres.fields import JSONField
from django.db.models import (
    Model,
    CharField,
    DecimalField,
    IntegerField,
    FileField,
    BooleanField,
    DateTimeField,
    ForeignKey,
    PROTECT,
    BigAutoField,
    TextChoices,
    FloatField,
)
from django.utils.translation import gettext_lazy as _

from katago_server.contrib.validators import FileValidator
from katago_server.runs.models import Run
from katago_server.trainings.models import Network
from katago_server.users.models import User

__ALL__ = ["TrainingGame", "RankingEstimationGame"]


def upload_sgf_to(instance, _filename):
    return os.path.join("games", f"{instance.uuid}.sgf")


validate_sgf = FileValidator(max_size=1024 * 1024 * 10, magic_types=("Smart Game Format (Go)",))


class AbstractGame(Model):
    """
    This class holds the common games properties
    """

    class Meta:
        abstract = True
        ordering = "id"

    class GamesResult(TextChoices):
        WHITE = "W", _("White")
        BLACK = "B", _("Black")
        DRAW = "0", _("Draw (Jigo)")
        NO_RESULT = "-", _("No Result (Moshoubou)")  # https://senseis.xmp.net/?NoResult

    # We expect a large number of games so lets use BigInt
    id = BigAutoField(primary_key=True)
    run = ForeignKey(Run, verbose_name=_("run"), on_delete=PROTECT, related_name="%(class)s_games", db_index=True)
    # A game is submitted by an user
    created_at = DateTimeField(_("creation date"), auto_now_add=True, db_index=True)
    submitted_by = ForeignKey(User, verbose_name=_("submitted by"), on_delete=PROTECT, related_name="%(class)s_games", db_index=True)
    playouts_per_sec = FloatField(_("playout per second"), null=True)
    # Describe the board/game itself
    board_size_x = IntegerField(_("board absciss"), null=False, default=19)
    board_size_y = IntegerField(_("board ordinate"), null=False, default=19)
    handicap = IntegerField(_("nb of handicap stone"), null=False, default=0)
    komi = DecimalField(_("komi (white)"), max_digits=3, decimal_places=1, null=False, default=7.0)
    rules_params = JSONField(
        _("game rules"),
        help_text=_(
            "Depending on rule set, the ko (https://senseis.xmp.net/?Ko), the scoring (https://senseis.xmp.net/?Scoring), the group tax (https://senseis.xmp.net/?GroupTax) and the suicide (https://senseis.xmp.net/?Suicide) may have subtle difference. See more info here https://lightvector.github.io/KataGo/rules.html"
        ),
        default=dict,
        null=True,
        blank=True,
    )  # See https://lightvector.github.io/KataGo/rules.html
    # Some extra information about the game like the type
    # eg: komi compensated games, uncompensated games, asymmetric playout games, seki-training games
    game_extra_params = JSONField(
        _("extra game parameters regarding game, like number of playout"),
        help_text=_("Some parameters (like the playout) are randomized by katago engine"),
        default=dict,
        null=True,
        blank=True,
    )
    # The results
    result = CharField(_("game result"), max_length=15, choices=GamesResult.choices, db_index=True)
    score = DecimalField(_("game score"), max_digits=4, decimal_places=1, null=True, blank=True)
    has_resigned = BooleanField(_("game end up with resign"), default=False, db_index=True)
    # The networks related to this game
    white_network = ForeignKey(Network, verbose_name=_("network white"), on_delete=PROTECT, related_name="%(class)s_games_as_white", db_index=True)
    black_network = ForeignKey(Network, verbose_name=_("network black"), on_delete=PROTECT, related_name="%(class)s_games_as_black", db_index=True)
    # A game can be forked from an existing game or a initial situation
    initial_position_sgf_file = FileField(verbose_name=_("initial position, as sgf file"), null=True, blank=True)
    initial_position_extra_params = JSONField(verbose_name=_("initial position extra parameters"), default=dict, null=True, blank=True)
    # The result of the game is stored as an sgf file, always ready to be viewed
    sgf_file = FileField(_("resulting sgf file"), upload_to=upload_sgf_to, validators=(validate_sgf,),  max_length=200)
    # KataGo engine's Hash128 for the whole game.
    game_hash = CharField(_("game_hash from katago"), max_length=48, default="")

    @property
    def result_text(self):
        score = "R" if self.has_resigned else self.score
        return f"{self.result}+{score}" if self.result in [AbstractGame.GamesResult.BLACK, AbstractGame.GamesResult.WHITE] else self.result

    def __str__(self):
        return f"{self.id} ({self.result_text})"
