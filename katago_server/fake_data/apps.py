from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FakeDataConfig(AppConfig):
    name = "katago_server.fake_data"
    verbose_name = _("Fake Data")

    def ready(self):
        try:
            import katago_server.fake_data.signals  # noqa F401
        except ImportError:
            pass
