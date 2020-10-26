from django.views.generic import TemplateView
from django.db.models import Sum, Count, Q

from src.apps.games.models import GameCountByNetwork, GameCountByUser, RecentGameCountByUser
from src.apps.trainings.models import Network
from src.apps.runs.models import Run

from . import view_utils

class HomeView(TemplateView):
  template_name = "pages/home.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["top_recent_user_list"] = (
      RecentGameCountByUser
      .objects
      .all()
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
      .all()
      .aggregate(
        total_num_training_rows=Sum("total_num_training_rows"),
        total_num_training_games=Sum("total_num_training_games"),
        total_num_rating_games=Sum("total_num_rating_games"),
      )
    )

    context["num_total_contributors"] = (
      GameCountByUser
      .objects
      .filter(Q(total_num_training_games__gt=0) | Q(total_num_rating_games__gt=0))
      .values("username").distinct().count()
    )

    context["total_num_training_rows"] = all_games_stats["total_num_training_rows"]
    context["total_num_games"] = all_games_stats["total_num_training_games"] + all_games_stats["total_num_rating_games"]

    context["num_recent_contributors"] = (
      RecentGameCountByUser
      .objects
      .filter(Q(total_num_training_games__gt=0) | Q(total_num_rating_games__gt=0))
      .values("username").distinct().count()
    )

    recent_games_stats = (
      RecentGameCountByUser
      .objects
      .all()
      .aggregate(
        total_num_training_rows=Sum("total_num_training_rows"),
        total_num_training_games=Sum("total_num_training_games"),
        total_num_rating_games=Sum("total_num_rating_games"),
      )
    )
    context["num_recent_training_rows"] = recent_games_stats["total_num_training_rows"]
    context["num_recent_games"] = recent_games_stats["total_num_training_games"] + recent_games_stats["total_num_rating_games"]

    run = Run.objects.select_current()
    context["run"] = run
    if run:
      context["num_networks_this_run_excluding_random"] = Network.objects.filter(run=run,is_random=False).count()
      context["num_rating_games_this_run"] = (
        GameCountByNetwork
        .objects
        .filter(run=run)
        .aggregate(total_num_rating_games=Sum("total_num_rating_games"))
        ["total_num_rating_games"]
      )
      context["latest_network"] = Network.objects.filter(run=run).order_by("-created_at").first()

    return context
