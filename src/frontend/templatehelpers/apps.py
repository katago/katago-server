from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TemplateHelpersConfig(AppConfig):
    """
    An app to contain custom template tags and filters used in the frontend, since django
    requires that these are part of an app.
    """

    name = "src.frontend.templatehelpers"
    verbose_name = _("TemplateHelpers")

    def ready(self):
        try:
            import src.frontend.templatehelpers.signals  # noqa F401
        except ImportError:
            pass
