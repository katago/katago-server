from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from src.apps.runs.models import Run

from . import view_utils

class RunInfoView(TemplateView):
  template_name = "pages/run_info.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    run = get_object_or_404(Run, name=kwargs["run"])
    context["run"] = run
    context["is_older_run"] = run != Run.objects.select_current_or_latest()
    if run:
      view_utils.add_run_stats_context(run,context)
    return context
