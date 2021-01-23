import numpy as np
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import (
    AutoField,
    BooleanField,
    CharField,
    DateTimeField,
    FloatField,
    IntegerField,
    Model,
    QuerySet,
    TextChoices,
    TextField,
)
from django.utils.translation import gettext_lazy as _


class RunQuerySet(QuerySet):
    def select_current(self):
        """
        Select the last active run and return it, or else None

        :return: the current run
        """
        return self.filter(status=Run.RunStatus.ACTIVE).order_by("-created_at").first()

    def select_current_or_latest(self):
        """
        Select the last active run and return it, or else the most recent, run, or else None.
        Only returns None if there are no runs at all.
        """
        run = self.filter(status=Run.RunStatus.ACTIVE).order_by("-created_at").first()
        if run:
            return run
        return self.order_by("-created_at").first()


alphanumeric = RegexValidator(r"^[0-9a-zA-Z]*$", "Only alphanumeric characters are allowed.")


def validate_probability(value):
    if np.isnan(value) or value < 0 or value > 1:
        raise ValidationError(
            _("%(value)s must range from 0 to 1"),
            params={"value": value},
        )


def validate_positive(value):
    if np.isnan(value) or value < 0:
        raise ValidationError(
            _("%(value)s must be positive"),
            params={"value": value},
        )


def validate_non_negative(value):
    if np.isnan(value) or value < 0:
        raise ValidationError(
            _("%(value)s must be nonnegative"),
            params={"value": value},
        )


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
    status = CharField(
        _("run status"),
        max_length=15,
        choices=RunStatus.choices,
        db_index=True,
        default=RunStatus.INACTIVE,
    )
    name = CharField(
        _("name"),
        max_length=16,
        validators=[alphanumeric],
        help_text=_("Run name. Should be short - used as a prefix for model names, for files and directories, etc."),
        unique=True,
        db_index=True,
    )

    # Config
    data_board_len = IntegerField(
        _("dataBoardLen"),
        default=19,
        help_text=_("Max board size for npz tensors. Should never change mid-run."),
        validators=[validate_positive],
    )
    inputs_version = IntegerField(
        _("inputsVersion"),
        default=7,
        help_text=_("Version of neural net features that nets are trained with."),
        validators=[validate_positive],
    )
    max_search_threads_allowed = IntegerField(
        _("Maximum numSearchThreads"),
        default=8,
        help_text=_("Maximum search threads that server promises to never exceed."),
        validators=[validate_positive],
    )
    rating_game_probability = FloatField(
        _("Rating game probability"),
        help_text=_("Probability that a task is a rating game instead of a selfplay game."),
        default=0.1,
        validators=[validate_probability],
    )
    rating_game_high_elo_probability = FloatField(
        _("Rating game high Elo weight"),
        help_text=_("RELATIVE probability for high Elo rating game."),
        default=1.0,
        validators=[validate_non_negative],
    )
    rating_game_high_uncertainty_probability = FloatField(
        _("Rating game high uncertainty weight"),
        help_text=_("RELATIVE probability for high uncertainty rating game."),
        default=1.0,
        validators=[validate_non_negative],
    )
    rating_game_low_data_probability = FloatField(
        _("Rating game low data weight"),
        help_text=_("RELATIVE probability for low data rating game."),
        default=1.0,
        validators=[validate_non_negative],
    )
    selfplay_startpos_probability = FloatField(
        _("Selfplay startpos probability"),
        help_text=_("Probability that a selfplay game uses a starting position, if there are any."),
        default=0.0,
        validators=[validate_probability],
    )
    rating_game_variability_scale = FloatField(
        _("Rating game variability scale"),
        help_text=_(
            "Rating games normally choose opponent proportional to variance of predicted result, set larger to add more variability, smaller to scale it down."
        ),
        default=1.0,
        validators=[validate_positive],
    )
    virtual_draw_strength = FloatField(
        _("Virtual draw strength"),
        help_text=_(
            "Between networks and parent networks, add a prior of equal Elo with strength equal to this many virtual draws."
        ),
        default=4.0,
        validators=[validate_positive],
    )
    elo_number_of_iterations = IntegerField(
        _("Elo computation number of iterations"),
        help_text=_("How many iterations to use per celery task to compute log_gammas and Elos."),
        default=10,
        validators=[validate_positive],
    )
    selfplay_client_config = TextField(
        _("Selfplay game config"),
        help_text=_("Client config for selfplay games."),
        default="FILL ME",
    )
    rating_client_config = TextField(
        _("Rating game config"),
        help_text=_("Client config for rating games."),
        default="FILL ME",
    )
    git_revision_hash_whitelist = TextField(
        _("Allowed client git revisions"),
        help_text=_("Newline-separated whitelist of allowed client git revision hashes, hash comments."),
        default="",
    )
    restrict_to_user_whitelist = BooleanField(
        _("Restrict contributors?"),
        help_text=_("If true, restrict to specified allowed contributors."),
        default=False,
    )
    user_whitelist = TextField(
        _("Allowed contrbutors"),
        help_text=_("Newline-separated whitelist of usernames to allow, hash comments."),
        default="",
    )
    startpos_locked = BooleanField(
        _("StartPoses being updated?"),
        help_text=_("Are startposes in the middle of being updated?."),
        default=False,
    )
    startpos_total_weight = FloatField(
        _("Total weight of StartPoses"),
        help_text=_("Total cumulative weight of StartPoses last time they were updated."),
        default=-1,
    )
    min_network_usage_delay = FloatField(
        _("Min network usage delay"),
        help_text=_(
            "Minimum delay after upload in seconds to use networks for tasks. Randomized between min and max by client instance."
        ),
        default=0,
    )
    max_network_usage_delay = FloatField(
        _("Max network usage delay"),
        help_text=_(
            "Maximum delay after upload in seconds to use networks for tasks. Randomized between min and max by client instance."
        ),
        default=0,
    )

    def __str__(self):
        return f"{self.name}"

    def is_allowed_username(self, username):
        if not self.restrict_to_user_whitelist:
            return True
        user_whitelist = self.user_whitelist
        user_whitelist = [s for s in user_whitelist.split("\n") if len(s) > 0]
        user_whitelist = [s.split("#")[0].strip() for s in user_whitelist]
        user_whitelist = [s for s in user_whitelist if len(s) > 0]
        username = username.strip()
        return username in user_whitelist

    def is_git_in_whitelist(self, git_revision_hash):
        git_revision_hash_whitelist = self.git_revision_hash_whitelist
        git_revision_hash_whitelist = [s for s in git_revision_hash_whitelist.split("\n") if len(s) > 0]
        git_revision_hash_whitelist = [s.split("#")[0].strip().lower() for s in git_revision_hash_whitelist]
        git_revision_hash_whitelist = [s for s in git_revision_hash_whitelist if len(s) > 0]
        git_revision_hash = git_revision_hash.strip().lower()
        return git_revision_hash in git_revision_hash_whitelist
