from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AnnouncementsConfig(AppConfig):
    """
    Katago Announcements app handles some messages for the front page of the site
    """

    name = "src.apps.announcements"
    verbose_name = _("Announcements")

    def ready(self):
        try:
            import src.apps.announcements.signals  # noqa F401
        except ImportError:
            pass
