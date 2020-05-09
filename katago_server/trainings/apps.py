from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TrainingsConfig(AppConfig):
    """
    Katago Training app handles the creation and the rating update of network objects
    """

    name = "katago_server.trainings"
    verbose_name = _("Training")

    def ready(self):
        try:
            import katago_server.trainings.signals  # noqa F401
        except ImportError:
            pass
