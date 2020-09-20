from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StartPosesConfig(AppConfig):
    """
    Katago StartPos app handles startposes for selfplay
    """

    name = "src.apps.startposes"
    verbose_name = _("StartPoses")

    def ready(self):
        try:
            import src.apps.startposes.signals  # noqa F401
        except ImportError:
            pass
