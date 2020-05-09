import os

import uuid as uuid
from django.contrib.postgres.fields import JSONField
from django.core.files.storage import FileSystemStorage
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

__ALL__ = ["TrainingGame", "RatingGame"]

sgf_data_storage = FileSystemStorage(location="/data/games/sgf")


def upload_sgf_to(instance, _filename):
    return os.path.join("games", f"{instance.kg_game_uid}.sgf")


validate_sgf = FileValidator(max_size=1024 * 1024 * 10)


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

    id = BigAutoField(primary_key=True)
    run = ForeignKey(Run, verbose_name=_("run"), on_delete=PROTECT, related_name="%(class)s_games", db_index=True)
    created_at = DateTimeField(_("creation date"), auto_now_add=True, db_index=True)
    submitted_by = ForeignKey(User, verbose_name=_("submitted by"), on_delete=PROTECT, related_name="%(class)s_games", db_index=True)
    board_size_x = IntegerField(_("board size x"), null=False, default=19, help_text=_("Width of board"), db_index=True)
    board_size_y = IntegerField(_("board size y"), null=False, default=19, help_text=_("Height of board"), db_index=True)
    handicap = IntegerField(_("handicap"), null=False, default=0, help_text=_("Number of handicap stones, generally 0 or >= 2"), db_index=True)
    komi = DecimalField(_("komi"), max_digits=3, decimal_places=1, null=False, default=7.0, help_text=_("Number of points added to white's score"), db_index=True)
    rules = JSONField(
        _("rules"),
        help_text=_("Rules are described at https://lightvector.github.io/KataGo/rules.html"),
        default=dict,
        null=True,
        blank=True,
    )
    extra_metadata = JSONField(
        _("extra metadata"),
        help_text=_("Additional miscellaneous metadata about this game"),
        default=dict,
        null=True,
        blank=True,
    )

    winner = CharField(_("winner"), max_length=1, choices=GamesResult.choices, db_index=True)
    score = DecimalField(_("score"), max_digits=4, decimal_places=1, null=True, blank=True, help_text=_("Final white points minus black points"))
    resigned = BooleanField(_("resigned"), default=False, db_index=True, help_text=_("Did this game end in resignation?"))

    white_network = ForeignKey(Network, verbose_name=_("white player network"), on_delete=PROTECT, related_name="%(class)s_games_as_white", db_index=True)
    black_network = ForeignKey(Network, verbose_name=_("black player network"), on_delete=PROTECT, related_name="%(class)s_games_as_black", db_index=True)

    sgf_file = FileField(_("SGF file"), upload_to=upload_sgf_to, validators=(validate_sgf,), storage=sgf_data_storage, max_length=200)
    kg_game_uid = CharField(_("KG game uid"), max_length=48, default="", help_text=_("Game uid from KataGo client"), db_index=True)

    @property
    def result_text(self):
        score = "R" if self.resigned else self.score
        return f"{self.winner}+{score}" if self.winner in [AbstractGame.GamesResult.BLACK, AbstractGame.GamesResult.WHITE] else self.winner

    def __str__(self):
        return f"{self.id} ({self.result_text})"
