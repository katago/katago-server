import markdown
import bleach

from django.db.models import (
    Model,
    BooleanField,
    CharField,
    DateTimeField,
    IntegerField,
    TextField,
    BigAutoField,
)
from django.utils.translation import gettext_lazy as _

class Announcement(Model):
    """
    An announcement is a block of html text for the front page display.
    """

    class Meta:
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")
        ordering = ["-display_order"]

    id = BigAutoField(primary_key=True)
    created_at = DateTimeField(_("creation date"), auto_now_add=True, db_index=True)
    updated_at = DateTimeField(_("updated date"), auto_now=True, db_index=True)
    title = CharField(
        _("title"),
        null=False,
        blank=False,
        max_length=240,
        help_text=_("Title of the announcement section."),
        unique=True,
    )
    contents = TextField(
        _("contents"),
        null=False,
        blank=True,
        help_text=_("Markdown contents of the announcement section."),
        db_index=False,
    )
    display_order = IntegerField(
        _("display_order"),
        null=False,
        help_text=_("Order of sections. Smaller indices come first."),
        db_index=True,
        unique=True,
    )
    enabled = BooleanField(
        _("enabled"),
        help_text=_("Enable for display on front page?"),
        default=True,
        db_index=True,
    )
    notes = TextField(
        _("notes"), max_length=1024, null=False, blank=True, help_text=_("Private notes about this announcement"), db_index=False,
    )

    @property
    def rendered_contents_safe(self):
        return bleach.clean(markdown.markdown(self.contents), tags = bleach.sanitizer.ALLOWED_TAGS + ["p","br"])
