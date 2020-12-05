import os

from django.core.validators import RegexValidator
from django.db.models import (
    Model,
    BigIntegerField,
    FileField,
    CharField,
    DateTimeField,
    FloatField,
    ForeignKey,
    PROTECT,
    BigAutoField,
    BooleanField,
)
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from math import log10, e

from src.contrib.validators import FileValidator
from src.contrib.variable_storage_file_field import VariableStorageFileField
from src.apps.runs.models import Run
from src.apps.trainings.managers.network_pandas_manager import NetworkPandasManager
from src.apps.trainings.managers.network_queryset import NetworkQuerySet

from django.conf import settings
from django.core.files.storage import get_storage_class
network_filestorage_class = get_storage_class(settings.NETWORK_FILE_STORAGE)

def upload_network_to(instance, filename):
    if filename.endswith(".bin.gz"):
        return os.path.join("networks", "models", instance.run.name, f"{instance.name}.bin.gz")
    elif filename.endswith(".txt.gz"):
        return os.path.join("networks", "models", instance.run.name, f"{instance.name}.txt.gz")
    else:
        return os.path.join("networks", "models", instance.run.name, f"{instance.name}" + os.path.splitext(filename)[1])

def upload_network_zip_to(instance, filename):
    return os.path.join("networks", "zips", instance.run.name, f"{instance.name}" + os.path.splitext(filename)[1])


validate_gzip = FileValidator(max_size=1024 * 1024 * 1024, content_types=["application/gzip"])
validate_model_zip = FileValidator(max_size=1024 * 1024 * 1024 * 3 / 2, content_types=["application/zip"])
alphanumeric_and_dashes = RegexValidator(r"^[-0-9a-zA-Z]*$", "Only alphanumeric or dash characters are allowed.")


class Network(Model):
    """
    A network is an object that refers to a ML Neural Network.

    Network are used by client to generate go/baduk training games, associated with training data.
    Network are evaluated by rating games played by client a small percentage of times (10% of training games).

    The training data are used to generate new network by an external training loop.
    """

    objects = NetworkQuerySet.as_manager()
    pandas = NetworkPandasManager()

    class Meta:
        verbose_name = _("Network")
        verbose_name_plural = _("Networks")
        ordering = ["-created_at"]

    id = BigAutoField(primary_key=True)
    name = CharField(
        _("neural network name"), max_length=128, null=False, blank=False, validators=[alphanumeric_and_dashes], db_index=True, unique=True,
    )
    run = ForeignKey(Run, verbose_name=_("run"), on_delete=PROTECT, null=False, blank=False, related_name="%(class)s_games", db_index=True,)
    created_at = DateTimeField(_("creation date"), auto_now_add=True, db_index=True)

    parent_network = ForeignKey(
        "self", verbose_name=_("Parent network for BayesElo prior"), null=True, blank=True, related_name="variants", on_delete=PROTECT,
    )

    network_size = CharField(
        _("network size"), max_length=32, null=False, blank=False, help_text=_("String describing blocks and channels in network."), db_index=True,
    )

    train_step = BigIntegerField(_("train step"), null=True, blank=False, help_text=_("Number of training steps of network, according to training machine."),)
    total_num_data_rows = BigIntegerField(_("total num data rows"), null=True, blank=False, help_text=_("Total number of data rows training machine had to train this network."),)
    extra_stats = JSONField(
        _("extra stats"), help_text=_("Any extra stats or info automatedly produced by the training machine"), default=dict, null=True, blank=True,
    )

    notes = CharField(
        _("notes"), max_length=1024, default="", null=False, blank=True, help_text=_("Special notes or info about this network."), db_index=False,
    )
    is_random = BooleanField(
        _("random"), default=False, help_text=_("If true, this network represents just random play rather than an actual network"), db_index=True,
    )
    training_games_enabled = BooleanField(
        _("training games enabled"), default=True, help_text=_("If true, this network can be used for training games"), db_index=True,
    )
    rating_games_enabled = BooleanField(
        _("rating games enabled"), default=True, help_text=_("If true, this network can be used for rating games"), db_index=True,
    )
    model_file = VariableStorageFileField(
        verbose_name=_("model file url"),
        upload_to=upload_network_to,
        validators=[validate_gzip],
        max_length=200,
        null=False,
        blank=True,
        help_text=_("Url to download network model file."),
        storage=network_filestorage_class(),
    )
    model_file_bytes = BigIntegerField(_("model file bytes"), null=False, blank=False, help_text=_("Number of bytes in network model file."),)
    model_file_sha256 = CharField(
        _("model file SHA256"), max_length=64, null=False, blank=False, help_text=_("SHA256 hash of network model file for integrity verification."),
    )
    model_zip_file = VariableStorageFileField(
        verbose_name=_("model zip file url"),
        upload_to=upload_network_zip_to,
        validators=[validate_model_zip],
        max_length=200,
        null=False,
        blank=True,
        help_text=_("Url to download zipped network model file with also tensorflow weights."),
        storage=network_filestorage_class(),
    )

    log_gamma = FloatField(_("log gamma"), default=0, help_text=_("Estimated BayesElo strength of network."), db_index=True,)
    log_gamma_uncertainty = FloatField(_("log gamma uncertainty"), default=0, help_text=_("Estimated stdev of BayesElo strength of network."),)
    log_gamma_lower_confidence = FloatField(
        _("log gamma lower confidence"), default=0, db_index=True, help_text=_("Lower confidence bound on BayesElo strength of network."),
    )
    log_gamma_upper_confidence = FloatField(
        _("log gamma upper confidence"), default=0, db_index=True, help_text=_("Upper confidence bound on BayesElo strength of network."),
    )
    log_gamma_game_count = BigIntegerField(_("log gamma game count"), default=0, db_index=True, help_text=_("Number of real games used to compute log_gamma for this network."),)

    def __str__(self):
        return f"{self.name} ({self.elo}±{2 * self.elo_uncertainty})"

    @property
    def size(self):
        return f"{self.network_size}"

    @property
    def elo(self):
        return round(self.log_gamma * 400 * log10(e), ndigits=1)

    @property
    def elo_uncertainty(self):
        return round(self.log_gamma_uncertainty * 400 * log10(e), ndigits=1)

    @property
    def rating(self):
        return f"{self.elo} ± {2 * self.elo_uncertainty}"

    def clean(self):
        # Allow blank file only if random
        no_model_file = not self.model_file or len(self.model_file) <= 0
        if no_model_file and not self.is_random:
            raise ValidationError("model_file is only allowed to be blank when is_random is True")
