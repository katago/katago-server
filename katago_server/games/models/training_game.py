from django.core.files.storage import FileSystemStorage
from django.db.models import FileField
from django.utils.translation import gettext_lazy as _

from katago_server.contrib.validators import FileValidator
from katago_server.games.models.abstract_game import AbstractGame

training_data_storage = FileSystemStorage(location="/training_data")
validate_gzip = FileValidator(max_size=1024 * 1024 * 300, content_types=("application/zip",))


def upload_unpacked_training_to(instance, _filename):
    return f"{instance.uuid}.npz"


class TrainingGame(AbstractGame):
    class Meta:
        verbose_name = _("Game: Training")
        ordering = ['-created_at']

    unpacked_file = FileField(
        _("training data (npz)"), upload_to=upload_unpacked_training_to, validators=(validate_gzip,), storage=training_data_storage
    )
