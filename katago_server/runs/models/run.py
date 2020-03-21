import uuid as uuid

from django.db.models import Model, CharField, IntegerField, FileField, DateTimeField, UUIDField, FloatField, ForeignKey, PROTECT
from django.utils.translation import gettext_lazy as _


class Run(Model):
    created_at = DateTimeField(_("creation date"), auto_now_add=True)
    name = CharField(_("name"), max_length=64)




