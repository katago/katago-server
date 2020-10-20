
from django.shortcuts import get_object_or_404
from src.apps.runs.models import Run

def set_current_run_or_run_from_url_for_view_get_queryset(view):
  """Helper for implementing get_queryset in a view that cares about the run.

  Sets view.run to:
    * The run specified by the url (from view.kwargs)
    * Or else, the current run if there is a current active run
    * Or else, None

  Sets view.viewing_current_run to False if the run was in the url, else True.
  """
  if view.kwargs["run"] is None:
    view.run = Run.objects.select_current()
    view.viewing_current_run = True
  else:
    view.run = get_object_or_404(Run, name=view.kwargs["run"])
    view.viewing_current_run = False


def add_other_runs_context(view,context):
  """Helper for implementing get_context_data in a view that cares about the run.
  Sets fields within context for use for rendering within a template for the view:
  "run" - view.run, the current run to display data for.
  "viewing_current_run" - whether it was specified in the url or not.
  "other_runs_to_show" - list of additional runs to provide links to the data for
  """
  context["run"] = view.run
  context["viewing_current_run"] = view.viewing_current_run
  context["other_runs_to_show"] = []
  run_count = Run.objects.count()
  show_other_runs = (
    (view.viewing_current_run and run_count > 1) or
    (view.viewing_current_run and run_count == 1 and view.run is None)
  )
  if show_other_runs:
    context["other_runs_to_show"] = list(Run.objects.order_by("-created_at"))
    if view.run is not None:
      context["other_runs_to_show"] = [run for run in context["other_runs_to_show"] if run.name != view.run.name]
