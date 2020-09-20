from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DistributedEffortsConfig(AppConfig):
    """
    Katago DistributedEfforts app handle client request for work to be done
    and dynamically return training or rating game parameters.
    """

    name = "src.apps.distributed_efforts"
    verbose_name = _("Distributed efforts")

    def ready(self):
        try:
            import src.apps.distributed_efforts.signals  # noqa F401
        except ImportError:
            pass
