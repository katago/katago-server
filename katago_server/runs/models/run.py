from django.db.models import Model, CharField, IntegerField, DateTimeField, TextChoices, AutoField, QuerySet
from django.utils.translation import gettext_lazy as _


class RunQuerySet(QuerySet):
    def select_current(self):
        return self.filter(status=Run.RunStatus.ACTIVE).order_by("-created_at").first()


class Run(Model):
    objects = RunQuerySet.as_manager()

    class RunStatus(TextChoices):
        ACTIVE = "Active", _("Active")

    id = AutoField(primary_key=True)
    created_at = DateTimeField(_("creation date"), auto_now_add=True, db_index=True)
    status = CharField(_("run status"), max_length=15, choices=RunStatus.choices, db_index=True, default=RunStatus.ACTIVE)
    name = CharField(_("name"), max_length=64)
    # Config
    data_board_len = IntegerField(_("data board len"), default=19)
    inputs_version = IntegerField(_("inputs version for model features"), default=7)
    max_search_threads_allowed = IntegerField(_("max search threads server promises to never exceed"), default=8)

    def __str__(self):
        return f"run-{self.id}: {self.name}"
