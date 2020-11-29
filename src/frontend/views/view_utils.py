import math

from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404

from src.apps.games.models import GameCountByNetwork, GameCountByUser, RecentGameCountByUser
from src.apps.trainings.models import Network
from src.apps.runs.models import Run

def set_current_run_or_run_from_url_for_view_get_queryset(view):
  """Helper for implementing get_queryset in a view that cares about the run.

  Sets view.current_run to the current active or latest run, if any.

  Sets view.run to:
    * The run specified by the url (from view.kwargs)
    * Or else, the current run.
    * Or else, None

  Sets view.run_specified_in_url to True if the run was in the url, else False.
  """
  view.current_run = Run.objects.select_current_or_latest()
  if view.kwargs["run"] is None:
    view.run = view.current_run
    view.run_specified_in_url = False
  else:
    view.run = get_object_or_404(Run, name=view.kwargs["run"])
    view.run_specified_in_url = True


def add_run_stats_context(run, context):
  """Add all the detailed summary stats about a run and its networks and games.
  For use on homepage or run detail view."""

  context["run"] = run

  context["top_recent_user_list"] = (
    RecentGameCountByUser
    .objects
    .filter(run=run)
    .values("username")
    .annotate(
      total_num_training_rows=Sum("total_num_training_rows"),
      total_num_training_games=Sum("total_num_training_games"),
      total_num_rating_games=Sum("total_num_rating_games"),
    )
    .order_by("-total_num_training_rows")
    .all()[:15]
  )
  context["top_total_user_list"] = (
    GameCountByUser
    .objects
    .filter(run=run)
    .values("username")
    .annotate(
      total_num_training_rows=Sum("total_num_training_rows"),
      total_num_training_games=Sum("total_num_training_games"),
      total_num_rating_games=Sum("total_num_rating_games"),
    )
    .order_by("-total_num_training_rows")
    .all()[:15]
  )

  all_games_stats = (
    GameCountByNetwork
    .objects
    .filter(run=run)
    .aggregate(
      total_num_training_rows=Sum("total_num_training_rows"),
      total_num_training_games=Sum("total_num_training_games"),
      total_num_rating_games=Sum("total_num_rating_games"),
    )
  )

  context["num_total_contributors_this_run"] = (
    GameCountByUser
    .objects
    .filter(run=run)
    .filter(Q(total_num_training_games__gt=0) | Q(total_num_rating_games__gt=0))
    .values("username").distinct().count()
  )

  context["total_num_training_rows_this_run"] = all_games_stats["total_num_training_rows"]
  context["total_num_training_games_this_run"] = all_games_stats["total_num_training_games"]
  # Divide by 2 because each rating game appears twice, once for each network that played it
  context["total_num_rating_games_this_run"] = all_games_stats["total_num_rating_games"]  // 2

  recent_games_stats = (
    RecentGameCountByUser
    .objects
    .filter(run=run)
    .aggregate(
      total_num_training_rows=Sum("total_num_training_rows"),
      total_num_training_games=Sum("total_num_training_games"),
      total_num_rating_games=Sum("total_num_rating_games"),
    )
  )

  context["num_recent_contributors_this_run"] = (
    RecentGameCountByUser
    .objects
    .filter(run=run)
    .filter(Q(total_num_training_games__gt=0) | Q(total_num_rating_games__gt=0))
    .values("username").distinct().count()
  )

  context["num_recent_training_rows_this_run"] = recent_games_stats["total_num_training_rows"]
  context["num_recent_training_games_this_run"] = recent_games_stats["total_num_training_games"]
  context["num_recent_rating_games_this_run"] = recent_games_stats["total_num_rating_games"]

  context["num_networks_this_run_excluding_random"] = Network.objects.filter(run=run,is_random=False).count()

  context["latest_network"] = Network.objects.filter(run=run).order_by("-created_at").first()
  # Arbitrary reasonable cap on the uncertainty we will tolerate when trying to report a strongest network
  max_uncertainty_elo = 100
  context["strongest_confident_network"] = (
    Network
    .objects
    .filter(run=run, log_gamma_uncertainty__lte=(max_uncertainty_elo / (400.0 * math.log10(math.e))))
    .order_by("-log_gamma_lower_confidence").first()
  )
