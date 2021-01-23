from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from src.apps.games.models import GameCountByNetwork, RatingGame, TrainingGame
from src.apps.runs.models import Run
from src.apps.trainings.models import Network
from src.apps.users.models import User
from src.frontend.utils import parse_util

from . import view_utils


class GameNetworkGroupsView(ListView):
    template_name = "pages/game_network_groups.html"
    context_object_name = "group_list"

    def get_queryset(self):
        view_utils.set_current_run_or_run_from_url_for_view_get_queryset(self)
        if self.run is None:
            return []
        return GameCountByNetwork.objects.filter(run=self.run).order_by("-network_created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["run"] = self.run
        context["current_run"] = self.current_run
        context["is_older_run"] = self.run != self.current_run
        context["show_older_runs"] = Run.objects.count() > 1
        return context


class GamesListByNetworkView(ListView):
    template_name = "pages/games_list_by_network.html"
    paginate_by = 100

    def get_queryset(self):
        self.run = get_object_or_404(Run, name=self.kwargs["run"])
        self.network = get_object_or_404(Network, name=self.kwargs["network"])
        if self.network.run != self.run:
            raise Http404("Network exists but is from the wrong run")

        if self.kwargs["kind"] == "training":
            games = (
                TrainingGame.objects.filter(white_network=self.network)
                .order_by("-created_at")
                .prefetch_related("submitted_by")
            )
        else:
            wgames = RatingGame.objects.filter(white_network=self.network).prefetch_related(
                "submitted_by", "black_network", "white_network"
            )
            bgames = RatingGame.objects.filter(black_network=self.network).prefetch_related(
                "submitted_by", "black_network", "white_network"
            )
            games = wgames.union(bgames).order_by("-created_at")
        return games

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["run"] = self.run
        context["network"] = self.network
        context["kind"] = self.kwargs["kind"]
        if self.kwargs["kind"] == "training":
            context["list_url_name"] = "training_games_list_by_network"  # urls.py
        else:
            context["list_url_name"] = "rating_games_list_by_network"  # urls.py
        return context


class GamesListByUserView(ListView):
    template_name = "pages/games_list_by_user.html"
    paginate_by = 100

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs["user"])

        if self.kwargs["kind"] == "training":
            games = (
                TrainingGame.objects.filter(submitted_by=self.user)
                .order_by("-created_at")
                .prefetch_related("run", "black_network", "white_network")
            )
        else:
            games = (
                RatingGame.objects.filter(submitted_by=self.user)
                .order_by("-created_at")
                .prefetch_related("run", "black_network", "white_network")
            )
        return games

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user
        context["kind"] = self.kwargs["kind"]
        if self.kwargs["kind"] == "training":
            context["list_url_name"] = "training_games_list_by_user"  # urls.py
        else:
            context["list_url_name"] = "rating_games_list_by_user"  # urls.py
        return context


class SgfDetailView(DetailView):
    template_name = "pages/sgfplayer.html"
    context_object_name = "game"

    def get_object(self, **kwargs):
        id = parse_util.parse_int_or_404(self.kwargs["id"])
        if self.kwargs["kind"] == "training":
            return get_object_or_404(TrainingGame, id=id)
        else:
            return get_object_or_404(RatingGame, id=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["kind"] = self.kwargs["kind"]
        return context
