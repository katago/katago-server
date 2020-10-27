from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.db.models import Sum

from src.apps.games.models import GameCountByUser, RecentGameCountByUser
from src.apps.runs.models import Run

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
    context["has_multiple_runs"] = Run.objects.count() > 1
    context["top_recent_user_list"] = (
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
      .all()[:30]
    )

    return context


class ContributionsByRunView(ListView):
  template_name = "pages/contributions_by_run.html"
  context_object_name = "all_time_user_list"

  def get_queryset(self):
    self.run = get_object_or_404(Run, name=self.kwargs["run"])
    self.current_run = Run.objects.select_current_or_latest()
    return \
      GameCountByUser \
      .objects \
      .filter(run=self.run) \
      .values("username") \
      .annotate(
        total_num_training_rows=Sum("total_num_training_rows"),
        total_num_training_games=Sum("total_num_training_games"),
        total_num_rating_games=Sum("total_num_rating_games"),
      ) \
      .order_by("-total_num_training_rows")

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["top_recent_user_list"] = (
      RecentGameCountByUser \
      .objects \
      .filter(run=self.run) \
      .values("username") \
      .annotate(
        total_num_training_rows=Sum("total_num_training_rows"),
        total_num_training_games=Sum("total_num_training_games"),
        total_num_rating_games=Sum("total_num_rating_games"),
      ) \
      .order_by("-total_num_training_rows")
      .all()[:30]
    )

    context["run"] = self.run
    context["current_run"] = self.current_run
    context["is_older_run"] = self.run != self.current_run
    context["show_older_runs"] = Run.objects.count() > 1
    return context
