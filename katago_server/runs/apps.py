from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RunsConfig(AppConfig):
    name = "katago_server.runs"
    verbose_name = _("Runs")

    def ready(self):
        try:
            import katago_server.runs.signals  # noqa F401
        except ImportError:
            pass
