from django.db.models import (
    Model,
    CharField,
    IntegerField,
    FloatField,
    TextField,
    DateTimeField,
    TextChoices,
    AutoField,
    QuerySet,
)
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


# TODO: investigate extracting this class to a manager directory, like games
class RunQuerySet(QuerySet):
    def select_current(self):
        """
        Select the last active run and return it

        :return: the current run
        """
        return self.filter(status=Run.RunStatus.ACTIVE).order_by("-created_at").first()


alphanumeric = RegexValidator(r"^[0-9a-zA-Z]*$", "Only alphanumeric characters are allowed.")


class Run(Model):
    """
    A runs is a conceptual group of games and model. It allows katago server to perform
    successive or concurrent (need some work) experiment while distinguishing associated objects.
    """

    class Meta:
        verbose_name = _("Run")
        ordering = ["-created_at"]

    objects = RunQuerySet.as_manager()

    class RunStatus(TextChoices):
        ACTIVE = "Active", _("Active")
        INACTIVE = "Inactive", _("Inactive")

    id = AutoField(primary_key=True)
    created_at = DateTimeField(_("creation date"), auto_now_add=True, db_index=True)
    status = CharField(_("run status"), max_length=15, choices=RunStatus.choices, db_index=True, default=RunStatus.INACTIVE,)
    name = CharField(
        _("name"),
        max_length=16,
        validators=[alphanumeric],
        help_text=_("Run name. Should be short - used as a prefix for model names, for files and directories, etc."),
        unique=True,
        db_index=True,
    )

    # Config
    data_board_len = IntegerField(_("dataBoardLen"), default=19, help_text=_("Max board size for npz tensors. Should never change mid-run."),)
    inputs_version = IntegerField(_("inputsVersion"), default=7, help_text=_("Version of neural net features that nets are trained with."),)
    max_search_threads_allowed = IntegerField(
        _("Maximum numSearchThreads"), default=8, help_text=_("Maximum search threads that server promises to never exceed."),
    )
    rating_game_probability = FloatField(
        _("Rating game probability"), help_text=_("Probability that a task is a rating game instead of a selfplay game."), default=0.1,
    )
    rating_game_high_elo_probability = FloatField(
        _("Rating game high Elo probability"),
        help_text=_("Rating games are randomly selected to either be high_elo or highest_uncertainty"),
        default=0.5,
    )
    virtual_draw_strength = FloatField(
        _("Virtual draw strength"),
        help_text=_("Between networks and parent networks, add a prior of equal Elo with strength equal to this many virtual draws"),
        default=4.0,
    )
    selfplay_client_config = TextField(_("Selfplay game config"), help_text=_("Client config for selfplay games"), default="FILL ME",)
    rating_client_config = TextField(_("Rating game config"), help_text=_("Client config for rating games"), default="FILL ME",)
    git_revision_hash_whitelist = TextField(_("Allowed client git revisions"), help_text=_("Newline-separated whitelist of allowed client git revision hashes"), default="",)

    def __str__(self):
        return f"{self.name}"
