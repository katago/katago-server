import uuid

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, UUIDField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    """
    An User is a registered account that can create games or, if super user, create new networks
    """

    class Meta:
        verbose_name = _("User")
        ordering = ["-date_joined"]

    # Uses uuid for security
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(_("Name of User"), blank=True, max_length=255)

