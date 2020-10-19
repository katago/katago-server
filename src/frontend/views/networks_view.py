from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import Http404

from src.apps.trainings.models import Network
from src.apps.runs.models import Run

class NetworksView(ListView):
  template_name = "pages/networks.html"
  context_object_name = "network_list"

  def get_queryset(self):
    if self.kwargs["run"] is None:
      self.run = Run.objects.select_current()
      self.viewing_current_run = True
    else:
      self.run = get_object_or_404(Run, name=self.kwargs["run"])
      self.viewing_current_run = False

    if self.run is None:
      return []
    return Network.objects.filter(run=self.run).order_by("-created_at")


  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["run"] = self.run
      context["viewing_current_run"] = self.viewing_current_run
      context["other_runs_to_show"] = []
      run_count = Run.objects.count()
      show_other_runs = (
        (self.viewing_current_run and run_count > 1) or
        (self.viewing_current_run and run_count == 1 and self.run is None)
      )
      if show_other_runs:
        context["other_runs_to_show"] = list(Run.objects.order_by("-created_at"))
        if self.run is not None:
          context["other_runs_to_show"] = [run for run in context["other_runs_to_show"] if run.name != self.run.name]
      return context
