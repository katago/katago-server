import os

from django.core.files.storage import FileSystemStorage
from django.db.models import FileField
from django.utils.translation import gettext_lazy as _

from katago_server.contrib.validators import FileValidator
from katago_server.games.models.abstract_game import AbstractGame

training_data_storage = FileSystemStorage(location="/data/training_npz", base_url="/media/")
validate_zip = FileValidator(max_size=1024 * 1024 * 300, content_types=("application/zip",))


def upload_training_data_to(instance: AbstractGame, _filename):
    return os.path.join(instance.run.name, instance.white_network.name, f"{instance.kg_game_uid}.npz")


class TrainingGame(AbstractGame):
    """
    A training game involves one network that plays both for black and white and is associated to numpy (npz) data used by the training loop
    """

    class Meta:
        verbose_name = _("Training game")
        ordering = ["-created_at"]

    training_data_file = FileField(
        _("training data (npz)"),
        upload_to=upload_training_data_to,
        validators=(validate_zip,),
        storage=training_data_storage,
        max_length=200,
        blank=False,
        null=False,
    )
