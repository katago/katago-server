from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GamesConfig(AppConfig):
    name = "katago_server.games"
    verbose_name = _("Users")

    def ready(self):
        try:
            import katago_server.games.signals  # noqa F401
        except ImportError:
            pass
