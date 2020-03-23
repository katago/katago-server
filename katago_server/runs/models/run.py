import uuid as uuid

from django.db.models import Model, CharField, IntegerField, FileField, DateTimeField, UUIDField, FloatField, ForeignKey, PROTECT
from django.utils.translation import gettext_lazy as _


class Run(Model):
    created_at = DateTimeField(_("creation date"), auto_now_add=True)
    name = CharField(_("name"), max_length=64)
    data_board_len = IntegerField(_("data board len"), default=19)
    inputs_version = IntegerField(_("inputs version for model features"), default=7)
    max_search_threads_allowed = IntegerField(_("max search threads server promises to never exceed"), default=8)
