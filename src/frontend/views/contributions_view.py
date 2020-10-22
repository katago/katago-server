from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import Http404

from src.apps.runs.models import Run
from src.apps.users.models import User
from src.apps.games.models import GameCountByUser

from . import view_utils

class ContributionsView(ListView):
  template_name = "pages/contributions.html"
  context_object_name = "user_list"

  def get_queryset(self):
    view_utils.set_current_run_or_run_from_url_for_view_get_queryset(self)
    if self.run is None:
      return []
    return GameCountByUser.objects.filter(run=self.run).order_by("-total_num_training_games")


  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    view_utils.add_other_runs_context(self,context)
    return context
