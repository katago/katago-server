from django.views.generic import TemplateView

from src.apps.runs.models import Run

from . import view_utils

class HomeView(TemplateView):
  template_name = "pages/home.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    run = Run.objects.select_current_or_latest()

    context["run"] = run
    if run:
      view_utils.add_run_stats_context(run,context)

    context["show_older_runs"] = Run.objects.count() > 1
    return context
