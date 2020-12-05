from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError

from src.apps.games.managers.rating_game_pandas_manager import RatingGamePandasManager
from src.apps.games.models.abstract_game import AbstractGame


class RatingGame(AbstractGame):
    """
    A rating game involves two different networks and is not used for training but for strength estimation
    """

    objects = Manager()
    pandas = RatingGamePandasManager()

    class Meta:
        verbose_name = _("Rating game")
        ordering = ["-created_at"]

    def clean(self):
        # Ratings games must involve distinct networks
        if self.white_network == self.black_network:
            raise ValidationError("Ratings games cannot be between a network and itself")

    def save(self, *args, **kwargs):
        return super(RatingGame, self).save(*args, **kwargs)
