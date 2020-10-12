import os

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
)
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from src.contrib.validators import FileValidator
from src.apps.runs.models import Run
from src.apps.trainings.models import Network
from src.apps.users.models import User

__ALL__ = ["TrainingGame", "RatingGame"]

def upload_sgf_to(instance, _filename):
    if instance.white_network.name == instance.black_network.name:
        return os.path.join("games", instance.run.name, instance.white_network.name, instance.created_at.strftime("%Y-%m-%d"), f"{instance.kg_game_uid}.sgf")
    else:
        return os.path.join("games", instance.run.name, "versus", instance.white_network.name, instance.created_at.strftime("%Y-%m-%d"), f"{instance.kg_game_uid}.sgf")


validate_sgf = FileValidator(max_size=1024 * 200, magic_types=("Smart Game Format (Go)",))

def validate_board_size(value):
    if value < 3 or value > 39:
        raise ValidationError(
            _('%(value)s must range from 3 to 39'),
            params={'value': value},
        )

def validate_handicap(value):
    if value < 0 or value > 13:
        raise ValidationError(
            _('%(value)s must range from 0 to 13'),
            params={'value': value},
        )

def validate_game_length(value):
    if value < 0 or value > 50000:
        raise ValidationError(
            _('%(value)s must range from 0 to 50000'),
            params={'value': value},
        )

def validate_komi(value):
    if value < -1000 or value > 1000:
        raise ValidationError(
            _('%(value)s must range from -1000 to 1000'),
            params={'value': value},
        )
    if round(value * 2) != value * 2:
        raise ValidationError(
            _('%(value)s must be an integer or a half-integer'),
            params={'value': value},
        )

def validate_score(value):
    if value is not None:
        if value < -10000 or value > 10000:
            raise ValidationError(
                _('%(value)s must range from -10000 to 10000'),
                params={'value': value},
            )
        if round(value * 2) != value * 2:
            raise ValidationError(
                _('%(value)s must be an integer or a half-integer'),
                params={'value': value},
            )

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
    run = ForeignKey(Run, verbose_name=_("run"), on_delete=PROTECT, related_name="%(class)s_games", db_index=True,)
    created_at = DateTimeField(_("creation date"), auto_now_add=True, db_index=True)
    submitted_by = ForeignKey(User, verbose_name=_("submitted by"), on_delete=PROTECT, related_name="%(class)s_games", db_index=True,)
    board_size_x = IntegerField(_("board size x"), null=False, default=19, validators=[validate_board_size], help_text=_("Width of board"), db_index=True,)
    board_size_y = IntegerField(_("board size y"), null=False, default=19, validators=[validate_board_size], help_text=_("Height of board"), db_index=True,)
    handicap = IntegerField(_("handicap"), null=False, default=0, validators=[validate_handicap], help_text=_("Number of handicap stones, generally 0 or >= 2"), db_index=True,)
    komi = DecimalField(
        _("komi"), max_digits=4, decimal_places=1, null=False, default=7.0, validators=[validate_komi], help_text=_("Number of points added to white's score"), db_index=True,
    )
    rules = JSONField(
        _("rules"), help_text=_("Rules are described at https://lightvector.github.io/KataGo/rules.html"), default=dict, null=True, blank=True,
    )
    extra_metadata = JSONField(
        _("extra metadata"), help_text=_("Additional miscellaneous metadata about this game"), default=dict, null=True, blank=True,
    )

    winner = CharField(_("winner"), max_length=1, choices=GamesResult.choices, db_index=True)
    score = DecimalField(_("score"), max_digits=5, decimal_places=1, null=True, validators=[validate_score], blank=True, help_text=_("Final white points minus black points"),)
    resigned = BooleanField(_("resigned"), default=False, db_index=True, help_text=_("Did this game end in resignation?"),)
    game_length = IntegerField(_("game length"), null=False, default=0, validators=[validate_game_length], help_text=_("Length of game in ply"), db_index=True,)

    white_network = ForeignKey(
        Network, verbose_name=_("white player network"), on_delete=PROTECT, related_name="%(class)s_games_as_white", db_index=True,
    )
    black_network = ForeignKey(
        Network, verbose_name=_("black player network"), on_delete=PROTECT, related_name="%(class)s_games_as_black", db_index=True,
    )

    sgf_file = FileField(_("SGF file"), upload_to=upload_sgf_to, validators=[validate_sgf], max_length=200,)
    kg_game_uid = CharField(_("KG game uid"), max_length=48, default="", help_text=_("Game uid from KataGo client"), db_index=True,)

    @property
    def result_text(self):
        if self.resigned:
            return f"{self.winner}+R"
        if self.winner not in [AbstractGame.GamesResult.BLACK, AbstractGame.GamesResult.WHITE]:
            return self.winner

        if self.winner == AbstractGame.GamesResult.BLACK:
            score = -self.score
        else:
            score = self.score
        return f"{self.winner}+{score}"

    def __str__(self):
        return f"{self.kg_game_uid} ({self.result_text})"
