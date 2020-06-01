import os

from django.core.files.storage import FileSystemStorage
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
from django.utils.translation import gettext_lazy as _
from math import log10, e

from katago_server.contrib.validators import FileValidator
from katago_server.runs.models import Run
from katago_server.trainings.managers.network_pandas_manager import NetworkPandasManager
from katago_server.trainings.managers.network_queryset import NetworkQuerySet

network_data_storage = FileSystemStorage(location="/data/networks", base_url="/media/networks/")


def upload_network_to(instance, _filename):
    return os.path.join(instance.run.name, f"{instance.name}.bin.gz")


validate_gzip = FileValidator(max_size=1024 * 1024 * 1024, content_types=("application/gzip",))
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
    # TODO is it possible to make this the primary key?
    # Having a url like https://katago.tycoach.me/api/networks/2/ is not very useful if the intended name for users
    # to recognize the network is not "2", but rather this name.
    name = CharField(
        _("neural network name"), max_length=128, null=False, blank=False, validators=[alphanumeric_and_dashes], db_index=True, unique=True,
    )
    run = ForeignKey(Run, verbose_name=_("run"), on_delete=PROTECT, null=False, blank=False, related_name="%(class)s_games", db_index=True,)
    created_at = DateTimeField(_("creation date"), auto_now_add=True)

    parent_network = ForeignKey(
        "self", verbose_name=_("Parent network for BayesElo prior"), null=True, blank=True, related_name="variants", on_delete=PROTECT,
    )

    network_size = CharField(
        _("network size"), max_length=32, null=False, blank=False, help_text=_("String describing blocks and channels in network."), db_index=True,
    )
    is_random = BooleanField(
        _("random"), default=False, help_text=_("If true, this network represents just random play rather than an actual network"), db_index=True,
    )
    model_file = FileField(
        verbose_name=_("model file url"),
        upload_to=upload_network_to,
        validators=(validate_gzip,),
        storage=network_data_storage,
        max_length=200,
        null=False,
        blank=True,
        help_text=_("Url to download network model file."),
    )
    model_file_bytes = BigIntegerField(_("model file bytes"), null=False, blank=False, help_text=_("Number of bytes in network model file."),)
    model_file_sha256 = CharField(
        _("model file SHA256"), max_length=64, null=False, blank=False, help_text=_("SHA256 hash of network model file for integrity verification."),
    )

    log_gamma = FloatField(_("log gamma"), default=0, help_text=_("Estimated BayesElo strength of network."), db_index=True,)
    log_gamma_uncertainty = FloatField(_("log gamma uncertainty"), default=0, help_text=_("Estimated stdev of BayesElo strength of network."),)
    log_gamma_lower_confidence = FloatField(
        _("log gamma lower confidence"), default=0, db_index=True, help_text=_("Lower confidence bound on BayesElo strength of network."),
    )
    log_gamma_upper_confidence = FloatField(
        _("log gamma upper confidence"), default=0, db_index=True, help_text=_("Upper confidence bound on BayesElo strength of network."),
    )

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
        return f"{self.elo} ±{2 * self.elo_uncertainty}"

    def save(self, *args, **kwargs):
        is_creating_a_new_model = not self.pk
        if is_creating_a_new_model:
            # default the parent net to actual last net
            # TODO: We should let the api to create a model throw if there is no parent mode
            if not self.parent_network:
                self.parent_network = Network.objects.last()
        # Allow blank file only if random
        no_model_file = not self.model_file or len(self.model_file) <= 0
        if no_model_file and not self.is_random:
            raise ValueError("model_file is only allowed to be blank when is_random is True")

        return super(Network, self).save(*args, **kwargs)
