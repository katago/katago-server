from django.views.generic import ListView

from src.apps.runs.models import Run
from src.apps.trainings.models import Network

from . import view_utils


class NetworksView(ListView):
    template_name = "pages/networks.html"
    context_object_name = "network_list"

    def get_queryset(self):
        view_utils.set_current_run_or_run_from_url_for_view_get_queryset(self)
        if self.run is None:
            return []
        return Network.objects.filter(run=self.run).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["run"] = self.run
        context["current_run"] = self.current_run
        context["is_older_run"] = self.run != self.current_run
        context["show_older_runs"] = Run.objects.count() > 1
        return context
