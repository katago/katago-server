import os
import uuid as uuid

from django.apps import apps
from django.contrib.postgres.fields import JSONField
from django.db import transaction
from django.db.models import Model, QuerySet, CharField, FileField, DateTimeField, ForeignKey, BigAutoField, UUIDField, TextChoices, PROTECT
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from katago_server.contrib.validators import FileValidator
from katago_server.trainings.models import Network
from katago_server.users.models import User

# QUESTION (lightvector): What does this mean? Does this mean if the game doesn't complete within an hour, it is assumed to be forgotten?
# It should probably be more like 6 hours or 12 hours, just to be friendy to users with slow machines.
DEFAULT_EXPIRATION_DELTA = timezone.timedelta(hours=1)


def upload_initial_to(instance, _filename):
    return os.path.join("initial_position", f"{instance.uuid}.sgf")


validate_sgf = FileValidator(max_size=1024 * 1024 * 10, magic_types=("Smart Game Format (Go)",))


class DistributedTaskQuerySet(QuerySet):
    def get_one_unassigned_with_lock(self):
        self.select_for_update(skip_locked=True).filter(status=AbstractDistributedTask.Status.UNASSIGNED).first()


class AbstractDistributedTask(Model):
    """
    This class holds a predefined job that will be given in priority to fast client
    """

    objects = DistributedTaskQuerySet.as_manager()

    class Meta:
        abstract = True

    class Status(TextChoices):
        UNASSIGNED = "UNASSIGNED", _("Unassigned")
        ONGOING = "ONGOING", _("Ongoing")
        DONE = "DONE", _("Done")
        CANCELED = "CANCELED", _("Canceled")

    # We expect a large number of "DistributedTasks" so lets use BigInt
    id = BigAutoField(primary_key=True)
    uuid = UUIDField(_("unique identifier"), default=uuid.uuid4, db_index=True)
    status = CharField(_("task status"), max_length=15, choices=Status.choices, null=False, default=Status.UNASSIGNED)
    # a predefined task  get attributed to an user with some expiration
    created_at = DateTimeField(_("creation date"), auto_now_add=True)
    assigned_to = ForeignKey(User, verbose_name=_("assigned to"), on_delete=PROTECT, related_name="%(class)s_games", blank=True, null=True)
    assigned_at = DateTimeField(_("assignation date"), auto_now=True, blank=True, null=True)
    expire_at = DateTimeField(_("expiration date"), blank=True, null=True)
    # The networks related to this game
    white_network = ForeignKey(Network, verbose_name=_("network white"), on_delete=PROTECT, related_name="%(class)s_predefined_jobs_as_white")
    black_network = ForeignKey(Network, verbose_name=_("network black"), on_delete=PROTECT, related_name="%(class)s_predefined_jobs_as_black")
    # A PredefinedJob can be forked from an existing game or a initial situation
    initial_position_sgf_file = FileField(
        _("initial position, as sgf file"), upload_to=upload_initial_to, validators=(validate_sgf,), null=True, blank=True
    )
    initial_position_extra_params = JSONField(_("initial position extra parameters"), default=dict, null=True, blank=True)

    def assign_to(self, target_user):
        self.status = self.Status.ONGOING
        self.assigned_to = target_user
        self.assigned_at = timezone.now()
        self.expire_at = timezone.now() + DEFAULT_EXPIRATION_DELTA
        self.save()

    def __str__(self):
        return f"{self.uuid}"
