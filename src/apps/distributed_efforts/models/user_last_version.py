from django.db.models import (
    Model,
    OneToOneField,
    CharField,
    DateTimeField,
    CASCADE,
)
from django.utils.translation import gettext_lazy as _

from src.apps.users.models import User

class UserLastVersion(Model):
    """
    Tracks the last git version that each user seemed to be using when requesting tasks.
    """

    class Meta:
        verbose_name = _("UserLastVersion")
        verbose_name_plural = _("UserLastVersions")

    user = OneToOneField(User, verbose_name=_('User'), on_delete=CASCADE, primary_key=True)
    access_time = DateTimeField(_("Access time"), auto_now=True, db_index=False)
    git_revision = CharField(_("Git revision"), max_length=80, default="", null=False, blank=True, help_text=_("Git revision hash that user sent to server"), db_index=False)

