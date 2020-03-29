import os
import uuid as uuid
import re
from math import log10, e

from django.contrib.postgres.fields import JSONField
from django.db.models import Model, IntegerField, FileField, DateTimeField, UUIDField, FloatField, ForeignKey, PROTECT
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from katago_server.contrib.validators import FileValidator
from katago_server.trainings.managers.network_pd_manager import NetworkPdManager
from katago_server.trainings.managers.network_queryset import NetworkQuerySet

# QUESTION (lightvector): Why does the server need to be uploading networks anywhere? Shouldn't it be the
# case that simply networks are uploaded to the appropriate filestorage solution directly by training and
# appropriately the server is notified?
def upload_network_to(instance, _filename):
    return os.path.join("networks", f"{instance.uuid}.gz")

# QUESTION (lightvector): I added these functions, are they useful for you, or do we want to do this a different way?
# They will parse a string like "g170-b40c256x2-s2436610304-d726429752" and return
# the blocks and channels and other things.
def parse_katago_training_model_name(name):
    """Attempt to parse information out of KataGo's default model naming convention.
    Will return an empty dictionary if the model does not fit KataGo's normal naming convention."""
    pieces = name.split('-')
    if len(pieces) != 4 or pieces[1][0] != 'b' or 'c' not in pieces[1] or pieces[2][0] != 's' or pieces[3][0] != 'd':
        return {}
    try:
        parsed = {}
        parsed["run_name"] = pieces[0]
        matched = re.fullmatch(r"^b(\d+)c(\d+).*$",pieces[1])
        if matched is None:
            return {}
        parsed["nb_blocks"] = int(matched.group(1))
        parsed["nb_channels"] = int(matched.group(2))
        parsed["nb_trained_samples"] = int(pieces[2][1:])
        parsed["nb_data_samples"] = int(pieces[3][1:])
        return parsed
    except ValueError:
        return None


validate_zip = FileValidator(max_size=1024 * 1024 * 300, content_types=("application/zip",))


class Network(Model):
    """
    This class create a table to hold the different networks trained.

    In addition to the existing 'id' that django adds to every models:
    - 'uuid': represent a random name append to a model
    - 'nb_blocks' and 'nb_channels': the number of feature of the model (the size).
       The bigger the stronger but also the slower.
    - 'model_architecture_details' contains the other architecture detail
    - 'model_file' contains a link to the gziped file
    - 'ranking' which gives an indication of a network strength

    The "ranking" will be continuously updated, with bayesian-elo
    """

    objects = NetworkQuerySet.as_manager()
    pd = NetworkPdManager()

    class Meta:
        verbose_name = _("Network")
        verbose_name_plural = _("Networks")

    # QUESTION (lightvector): Do any changes need to be made such that this can be a different identifier supplied by the training process?
    uuid = UUIDField(_("unique identifier"), default=uuid.uuid4, db_index=True)
    created_at = DateTimeField(_("creation date"), auto_now_add=True)
    # QUESTION (lightvector): What is parent_network for?
    parent_network = ForeignKey("self", null=True, blank=True, related_name="variants", on_delete=PROTECT)
    # Some description of the network itself
    # QUESTION (lightvector): Theoretically one day we could have an architecture that is different than a resnet, do we want to make blocks optional?
    nb_blocks = IntegerField(_("number of blocks in network"))
    # QUESTION (lightvector): Not just theoretically, but actually it is experimentally possible for one to try networks with variable numbers of
    # channels in different layers of different blocks, like "wide" resnets and such. Do we want to make channels optional?
    nb_channels = IntegerField(_("number of channels in network"))
    model_architecture_details = JSONField(_("network architecture schema"), null=True, blank=True, default=dict)
    model_file = FileField(_("network Archive url"), upload_to=upload_network_to, validators=(validate_zip,))
    # And an estimation of the strength
    log_gamma = FloatField(_("log gamma"), default=0)
    log_gamma_uncertainty = FloatField(_("log gamma uncertainty"), default=0)
    log_gamma_lower_confidence = FloatField(
        _("minimal ranking"), default=0, db_index=True
    )  # used to select best sure network for training games (selfplay)
    log_gamma_upper_confidence = FloatField(
        _("maximal ranking"), default=0, db_index=True
    )  # used to select best unsure network for ranking games (matches)

    def __str__(self):
        # QUESTION (lightvector): self.id is a mismatch with uuid? Is there also an "id" field too?
        return f"net-{self.id} ({self.elo}±{2 * self.elo_uncertainty})"

    @property
    def size(self):
        return f"b{self.nb_blocks} c{self.nb_channels}"

    @property
    def elo(self):
        return round(self.log_gamma * 400 * log10(e), ndigits=1)

    @property
    def elo_uncertainty(self):
        return round(self.log_gamma_uncertainty * 400 * log10(e), ndigits=1)

    @property
    def ranking(self):
        return f"{self.elo} ±{2 * self.elo_uncertainty}"

    def save(self, *args, **kwargs):
        if not self.pk:  # only act on creation
            # default the parent net to actual last net
            if not self.parent_network:
                # Insert parent network
                self.parent_network = Network.objects.last()
        return super(Network, self).save(*args, **kwargs)
