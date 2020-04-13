import os
import uuid as uuid
import re
from math import log10, e

from django.contrib.postgres.fields import JSONField
from django.db.models import Model, IntegerField, FileField, CharField, DateTimeField, UUIDField, FloatField, ForeignKey, PROTECT
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from katago_server.contrib.validators import FileValidator
from katago_server.trainings.managers.network_pd_manager import NetworkPdManager
from katago_server.trainings.managers.network_queryset import NetworkQuerySet

def upload_network_to(instance, _filename):
    return os.path.join("networks", f"{instance.uuid}.gz")

# TODO use this
def parse_katago_training_model_name(name):
    """Attempt to parse information out of KataGo's default model naming convention.
    Will return an empty dictionary if the model does not fit KataGo's normal naming convention."""
    pieces = name.split('-')
    if len(pieces) != 4 or pieces[1][0] != 'b' or 'c' not in pieces[1] or pieces[2][0] != 's' or pieces[3][0] != 'd':
        return {}
    try:
        parsed = {}
        parsed["run_name"] = pieces[0]
        parsed["network_size"] = pieces[1]
        parsed["nb_trained_samples"] = int(pieces[2][1:])
        parsed["nb_data_samples"] = int(pieces[3][1:])
        return parsed
    except ValueError:
        return {}


validate_zip = FileValidator(max_size=1024 * 1024 * 300, content_types=("application/zip",))


class Network(Model):
    """
    This class create a table to hold the different networks trained.

    In addition to the existing 'id' that django adds to every models:
    - 'uuid': represent a random name append to a model
    - 'network_size': the number of feature of the model (the size).
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

    name = CharField(_("model name"), max_length=128, default="", db_index=True)
    created_at = DateTimeField(_("creation date"), auto_now_add=True)
    parent_network = ForeignKey("self", null=True, blank=True, related_name="variants", on_delete=PROTECT)
    # Some description of the network itself
    network_size = CharField(_("string describing blocks and channels in network"), max_length=32, default="")
    nb_parameters = IntegerField(_("number of parameters in network"), default=0)
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
        return f"net-{self.id} ({self.elo}±{2 * self.elo_uncertainty})"

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
    def ranking(self):
        return f"{self.elo} ±{2 * self.elo_uncertainty}"

    def save(self, *args, **kwargs):
        if not self.pk:  # only act on creation
            # default the parent net to actual last net
            if not self.parent_network:
                # Insert parent network
                self.parent_network = Network.objects.last()
        return super(Network, self).save(*args, **kwargs)
