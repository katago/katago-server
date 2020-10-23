from django.views.generic import ListView
from django.db.models import Sum

from src.apps.games.models import GameCountByUser, RecentGameCountByUser

from . import view_utils

class ContributionsView(ListView):
  template_name = "pages/contributions.html"
  context_object_name = "all_time_user_list"

  def get_queryset(self):
    return \
      GameCountByUser \
      .objects \
      .all() \
      .values("username") \
      .annotate(
        total_num_training_rows=Sum("total_num_training_rows"),
        total_num_training_games=Sum("total_num_training_games"),
        total_num_rating_games=Sum("total_num_rating_games"),
      ) \
      .order_by("-total_num_training_rows")

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["recent_user_list"] = (
      RecentGameCountByUser \
      .objects \
      .all() \
      .values("username") \
      .annotate(
        total_num_training_rows=Sum("total_num_training_rows"),
        total_num_training_games=Sum("total_num_training_games"),
        total_num_rating_games=Sum("total_num_rating_games"),
      ) \
      .order_by("-total_num_training_rows")
      .all()[:20]
    )

    return context
