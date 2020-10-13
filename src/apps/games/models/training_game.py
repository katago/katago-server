import os
import numpy as np
import zipfile
from io import BytesIO

from django.db.models import FileField, IntegerField
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete
from django.core.files.storage import default_storage

from src.contrib.validators import FileValidator
from src.apps.games.models.abstract_game import AbstractGame

validate_zip = FileValidator(max_size=1024 * 500, content_types=["application/zip"])

def validate_game_npzdata(training_data_file,run):
    npz_file = training_data_file
    max_size = 1024 * 500
    max_unzipped_size = 1024 * 1024 * 20

    data_board_len = run.data_board_len

    if npz_file.size > max_size:
        params = {
            "max_size": filesizeformat(max_size),
            "size": filesizeformat(npz_file.size),
        }
        raise ValidationError("NPZ file size is greater than %(max_size)s: size is %(size)s.", "max_size", params)
    zipped_contents = npz_file.read()

    try:
        with zipfile.ZipFile(BytesIO(zipped_contents), "r") as z:
            unzipped_size = 0
            for fileinfo in z.infolist():
                unzipped_size += fileinfo.file_size
    except Exception as e:
        raise ValidationError("Error reading NPZ contents: " + str(e))

    if unzipped_size > max_unzipped_size:
        params = {
            "max_unzipped_size": filesizeformat(max_unzipped_size),
            "unzipped_size": filesizeformat(unzipped_size),
        }
        raise ValidationError("NPZ unzipped file size is greater than %(max_unzipped_size)s: size is %(unzipped_size)s.", "max_unzipped_size", params)

    all_keys = [
        "binaryInputNCHWPacked",
        "globalInputNC",
        "policyTargetsNCMove",
        "globalTargetsNC",
        "scoreDistrN",
        "valueTargetsNCHW"
    ]
    try:
        with np.load(BytesIO(zipped_contents)) as npz:
            arrs = dict([(key,npz[key]) for key in all_keys])
    except Exception as e:
        raise ValidationError("Error reading NPZ contents: " + str(e))

    # Verify no nans in anything
    float_keys = [
        "globalInputNC",
        "globalTargetsNC",
    ]
    for key in float_keys:
        if np.isnan(np.sum(arrs[key])):
            raise ValidationError("NPZ file contains nan values")

    # Verify batch size
    num_rows = arrs["binaryInputNCHWPacked"].shape[0]
    for key in all_keys:
        if arrs[key].shape[0] != num_rows:
            raise ValidationError("NPZ file contains arrays with inconsistent dimension 0")

    # Verify dimensions
    if (arrs["binaryInputNCHWPacked"].shape[1] != 22 or
        arrs["globalInputNC"].shape[1] != 19 or
        arrs["policyTargetsNCMove"].shape[1] != 2 or
        arrs["policyTargetsNCMove"].shape[2] != data_board_len * data_board_len + 1 or
        arrs["globalTargetsNC"].shape[1] != 64 or
        arrs["scoreDistrN"].shape[1] != (data_board_len * data_board_len + 60) * 2 or
        arrs["valueTargetsNCHW"].shape[1] != 5 or
        arrs["valueTargetsNCHW"].shape[2] != data_board_len or
        arrs["valueTargetsNCHW"].shape[3] != data_board_len
    ):
        raise ValidationError("Unexpected NPZ array shapes")

    # Verify some magnitudes of things
    if (np.min(arrs["globalInputNC"][:,0:5]) < -5.0 or
        np.max(arrs["globalInputNC"][:,0:5]) > 5.0 or
        np.min(arrs["globalInputNC"][:,6:]) < -5.0 or
        np.max(arrs["globalInputNC"][:,6:]) > 5.0 or
        np.min(arrs["globalInputNC"][:,5]) < -60.0 or  # komi/20
        np.max(arrs["globalInputNC"][:,5]) > 60.0 or   # komi/20
        np.min(arrs["policyTargetsNCMove"]) < 0 or
        np.min(arrs["scoreDistrN"]) < 0 or
        np.min(arrs["valueTargetsNCHW"][:,0:4,:,:]) < -2.0 or
        np.max(arrs["valueTargetsNCHW"][:,0:4,:,:]) > 2.0
    ):
        raise ValidationError("Invalid NPZ values")

    if (np.min(arrs["globalTargetsNC"][:,0:3]) < -2.0 or
        np.max(arrs["globalTargetsNC"][:,0:3]) > 2.0 or
        np.min(arrs["globalTargetsNC"][:,3]) < -5000.0 or
        np.max(arrs["globalTargetsNC"][:,3]) > 5000.0 or
        np.min(arrs["globalTargetsNC"][:,4:7]) < -2.0 or
        np.max(arrs["globalTargetsNC"][:,4:7]) > 2.0 or
        np.min(arrs["globalTargetsNC"][:,7]) < -5000.0 or
        np.max(arrs["globalTargetsNC"][:,7]) > 5000.0 or
        np.min(arrs["globalTargetsNC"][:,8:11]) < -2.0 or
        np.max(arrs["globalTargetsNC"][:,8:11]) > 2.0 or
        np.min(arrs["globalTargetsNC"][:,11]) < -5000.0 or
        np.max(arrs["globalTargetsNC"][:,11]) > 5000.0 or
        np.min(arrs["globalTargetsNC"][:,12:15]) < -2.0 or
        np.max(arrs["globalTargetsNC"][:,12:15]) > 2.0 or
        np.min(arrs["globalTargetsNC"][:,15]) < -5000.0 or
        np.max(arrs["globalTargetsNC"][:,15]) > 5000.0 or
        np.min(arrs["globalTargetsNC"][:,16:19]) < -2.0 or
        np.max(arrs["globalTargetsNC"][:,16:19]) > 2.0 or
        np.min(arrs["globalTargetsNC"][:,19]) < -5000.0 or
        np.max(arrs["globalTargetsNC"][:,19]) > 5000.0 or
        np.min(arrs["globalTargetsNC"][:,20:22]) < -5000.0 or
        np.max(arrs["globalTargetsNC"][:,20:22]) > 5000.0 or
        np.min(arrs["globalTargetsNC"][:,23:35]) < -5.0 or
        np.max(arrs["globalTargetsNC"][:,23:35]) > 5.0 or
        np.min(arrs["globalTargetsNC"][:,36:41]) < 0.0 or
        np.max(arrs["globalTargetsNC"][:,36:41]) > 1.0 or
        np.min(arrs["globalTargetsNC"][:,36:41]) < 0.0 or
        np.max(arrs["globalTargetsNC"][:,36:41]) > 1.0
    ):
        raise ValidationError("Invalid NPZ global target values")


def validate_num_training_rows(value):
    if value < 0 or value > 10000:
        raise ValidationError(
            _('%(value)s must range from 0 to 10000'),
            params={'value': value},
        )

def upload_training_data_to(instance: AbstractGame, _filename):
    return os.path.join("training_npz", instance.run.name, instance.white_network.name, instance.created_at.strftime("%Y-%m-%d"), f"{instance.kg_game_uid}.npz")


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
        max_length=200,
        blank=False,
        null=False,
    )

    num_training_rows = IntegerField(_("num training rows"), null=False, default=32, validators=[validate_num_training_rows], help_text=_("Number of training rows in data file"), db_index=True,)

    def clean(self):
        validate_game_npzdata(self.training_data_file,self.run)

