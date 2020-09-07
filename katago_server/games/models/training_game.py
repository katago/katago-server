import os

from django.core.files.storage import FileSystemStorage
from django.db.models import FileField, IntegerField
from django.utils.translation import gettext_lazy as _

from katago_server.contrib.validators import FileValidator
from katago_server.games.models.abstract_game import AbstractGame

training_data_storage = FileSystemStorage(location="/data/training_npz", base_url="/media/training_npz/")
validate_zip = FileValidator(max_size=1024 * 500, content_types=["application/zip"])

def validate_num_training_rows(value):
    if value < 0 or value > 10000:
        raise ValidationError(
            _('%(value)s must range from 0 to 10000'),
            params={'value': value},
        )

def upload_training_data_to(instance: AbstractGame, _filename):
    return os.path.join(instance.run.name, instance.white_network.name, instance.created_at.strftime("%Y-%m-%d"), f"{instance.kg_game_uid}.npz")


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
        validators=[validate_zip],
        storage=training_data_storage,
        max_length=200,
        blank=False,
        null=False,
    )

    num_training_rows = IntegerField(_("num training rows"), null=False, default=32, validators=[validate_num_training_rows], help_text=_("Number of training rows in data file"), db_index=True,)
