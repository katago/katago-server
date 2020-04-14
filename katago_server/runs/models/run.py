from django.db.models import Model, CharField, IntegerField, DateTimeField, TextChoices
from django.utils.translation import gettext_lazy as _

from katago_server.runs.managers.run_queryset import RunQuerySet


class Run(Model):
    objects = RunQuerySet.as_manager()

    class RunStatus(TextChoices):
        ACTIVE = "Active", _("Active")

    created_at = DateTimeField(_("creation date"), auto_now_add=True, db_index=True)
    result = CharField(_("run status"), max_length=15, choices=RunStatus.choices, db_index=True)
    name = CharField(_("name"), max_length=64)
    # Config
    data_board_len = IntegerField(_("data board len"), default=19)
    inputs_version = IntegerField(_("inputs version for model features"), default=7)
    max_search_threads_allowed = IntegerField(_("max search threads server promises to never exceed"), default=8)
