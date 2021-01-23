import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models import CharField, UUIDField
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _


@deconstructible
class UnicodeUsernameValidatorNoAtSymbol(RegexValidator):
    regex = r"^[\w.+-]+\Z"
    message = _("Enter a valid username. This value may contain only letters, " "numbers, and ./+/-/_ characters.")
    flags = 0


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
    username = CharField(
        _("username"),
        error_messages={"unique": _("A user with that username already exists.")},
        help_text="Required. 60 characters or fewer. Letters, digits and ./+/-/_ only.",
        max_length=60,
        unique=True,
        validators=[
            UnicodeUsernameValidatorNoAtSymbol(),
            MinLengthValidator(3),
        ],
    )
