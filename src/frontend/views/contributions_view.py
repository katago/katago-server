from django.views.generic import ListView
from django.db.models import Sum

from src.apps.games.models import GameCountByUser

from . import view_utils

class ContributionsView(ListView):
  template_name = "pages/contributions.html"
  context_object_name = "user_list"

  def get_queryset(self):
    return \
      GameCountByUser \
      .objects \
      .all() \
      .values("username") \
      .annotate(total_num_training_games=Sum("total_num_training_games"), total_num_rating_games=Sum("total_num_rating_games")) \
      .order_by("-total_num_training_games")

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    return context
