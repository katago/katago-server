import os

from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete

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


@receiver(post_delete, sender=RatingGame)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.sgf_file:
        if os.path.isfile(instance.sgf_file.path):
            os.remove(instance.sgf_file.path)

@receiver(pre_save, sender=RatingGame)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = RatingGame.objects.get(pk=instance.pk).sgf_file
    except RatingGame.DoesNotExist:
        return False

    new_file = instance.sgf_file
    if old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
