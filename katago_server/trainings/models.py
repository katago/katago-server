import os
import uuid as uuid
from math import log10, e

from django.contrib.postgres.fields import JSONField
from django.db.models import Model, IntegerField, FileField, DateTimeField, UUIDField, FloatField, ForeignKey, PROTECT
from django.utils.translation import gettext_lazy as _

from katago_server.contrib.validators import FileValidator


def upload_network_to(instance, filename):
    return os.path.join("network", f"{instance.uuid}.gz")


validate_zip = FileValidator(max_size=1024*1024*300, content_types=("application/zip",))


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
    class Meta:
        verbose_name = _("Network")
        verbose_name_plural = _("Networks")

    uuid = UUIDField(_("unique identifier"), default=uuid.uuid4)
    created_at = DateTimeField(_("creation date"), auto_now_add=True)
    parent_network = ForeignKey("self", null=True, blank=True, related_name="variants", on_delete=PROTECT)
    # Some description of the network itself
    nb_blocks = IntegerField(_("number of blocks in network"))
    nb_channels = IntegerField(_("number of channels in network"))
    model_architecture_details = JSONField(_("network architecture schema"),  null=True, blank=True, default=dict)
    model_file = FileField(_("network Archive url"), upload_to=upload_network_to, validators=(validate_zip,))
    # And an estimation of the strength
    log_gamma = FloatField(_("log gamma"),  null=True, blank=True)
    log_gamma_uncertainty = FloatField(_("log gamma uncertainty"), null=True, blank=True)
    log_gamma_lower_confidence = FloatField(_("minimal ranking"), null=True, blank=True, db_index=True)  # used to select best sure network for training games (selfplay)
    log_gamma_upper_confidence = FloatField(_("maximal ranking"), null=True, blank=True, db_index=True)  # used to select best unsure network for ranking games (matches)

    def __str__(self):
        return f"net-{self.id} ({self.elo}±{ 2 * self.elo_uncertainty})"

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
