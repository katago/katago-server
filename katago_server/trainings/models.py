import uuid as uuid
from django.contrib.postgres.fields import JSONField
from django.db.models import Model, IntegerField, FileField, DateTimeField, UUIDField, DecimalField


class Network(Model):
    """
    This class create a table to hold the different networks trained.

    In addition to the existing 'id' that django adds to every models:
    - 'uuid': represent a random name append to a model
    - 'nb_blocks' and 'nb_channels': the number of feature of the model (the size).
       The bigger the stronger but also the slower.
    - 'model_architecture_details' contains the other architecture detail
    - 'model_file' contains a link to the gziped file
    - 'elo' which gives an indication of a network strength

    The elo will be continuously updated, with bayesian elo
    """
    uuid = UUIDField(default=uuid.uuid4)
    created_at = DateTimeField(auto_now_add=True)
    # Some description of the network itself
    nb_blocks = IntegerField()
    nb_channels = IntegerField()
    model_architecture_details = JSONField(default=dict)
    model_file = FileField()
    # And an estimation of the strength
    # TODO: add GIST KNN index, so we can pick a network closed to an elo (for matches or self-play)
    elo = DecimalField(decimal_places=2, max_digits=7)

    def __str__(self):
        return f"g{self.id}-{self.uuid} ({self.elo})"
