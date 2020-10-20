from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator

from src.apps.games.models import TrainingGame, RatingGame
from src.apps.trainings.models import Network
from src.apps.runs.models import Run
from src.apps.users.models import User

from . import view_utils

class GameNetworkGroupsView(ListView):
  template_name = "pages/game_network_groups.html"

  # Networks, not games, since we're listing games grouped by network
  context_object_name = "network_list"

  def get_queryset(self):
    view_utils.set_current_run_or_run_from_url_for_view_get_queryset(self)
    if self.run is None:
      return []
    # We're returning the networks, because we display games organized by network
    return Network.objects.filter(run=self.run).order_by("-created_at")


  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    view_utils.add_other_runs_context(self,context)
    return context


class GamesListByNetworkView(ListView):
  template_name = "pages/games_list_by_network.html"
  paginate_by = 100

  def get_queryset(self):
    self.run = get_object_or_404(Run, name=self.kwargs["run"])
    self.network = get_object_or_404(Network, name=self.kwargs["network"])

    if self.kwargs["kind"] == "training":
      games = TrainingGame.objects.filter(white_network=self.network).order_by("-created_at")
    else:
      wgames = RatingGame.objects.filter(white_network=self.network)
      bgames = RatingGame.objects.filter(black_network=self.network)
      games = wgames.union(bgames).order_by("-created_at")
    return games

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["run"] = self.run
      context["network"] = self.network
      context["kind"] = self.kwargs["kind"]
      if self.kwargs["kind"] == "training":
        context["list_url_name"] = "training_games_list_by_network" # urls.py
        context["sgfplayer_url_name"] = "sgfplayer_training" # urls.py
      else:
        context["list_url_name"] = "rating_games_list_by_network" # urls.py
        context["sgfplayer_url_name"] = "sgfplayer_rating" # urls.py
      return context

class GamesListByUserView(ListView):
  template_name = "pages/games_list_by_user.html"
  paginate_by = 100

  def get_queryset(self):
    self.run = get_object_or_404(Run, name=self.kwargs["run"])
    self.user = get_object_or_404(User, username=self.kwargs["user"])

    if self.kwargs["kind"] == "training":
      games = TrainingGame.objects.filter(submitted_by=self.user,run=self.run).order_by("-created_at")
    else:
      games = RatingGame.objects.filter(submitted_by=self.user,run=self.run).order_by("-created_at")
    return games

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["run"] = self.run
      context["user"] = self.user
      context["kind"] = self.kwargs["kind"]
      if self.kwargs["kind"] == "training":
        context["list_url_name"] = "training_games_list_by_user" # urls.py
        context["sgfplayer_url_name"] = "sgfplayer_training" # urls.py
      else:
        context["list_url_name"] = "rating_games_list_by_user" # urls.py
        context["sgfplayer_url_name"] = "sgfplayer_rating" # urls.py
      return context


class SgfDetailView(DetailView):
  template_name = "pages/sgfplayer.html"
  context_object_name = "game"

  def get_object(self, **kwargs):
    if self.kwargs["kind"] == "training":
      return get_object_or_404(TrainingGame, id=self.kwargs["id"])
    else:
      return get_object_or_404(RatingGame, id=self.kwargs["id"])

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["kind"] = self.kwargs["kind"]
      return context

