from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator

from src.apps.games.models import TrainingGame, RatingGame
from src.apps.trainings.models import Network
from src.apps.runs.models import Run

class GameNetworkGroupsView(ListView):

  def get_queryset(self):
    self.run = None
    self.viewing_current_run = False
    if "viewing_current_run" in self.kwargs and self.kwargs["viewing_current_run"]:
      self.run = Run.objects.select_current()
      self.viewing_current_run = self.kwargs["viewing_current_run"]
    else:
      if "run" not in self.kwargs:
        raise Http404("Run not specified")
      self.run = get_object_or_404(Run, name=self.kwargs["run"])

    if self.run is None:
      return []

    # We're returning the networks, because we display games organized by network
    return Network.objects.filter(run=self.run).order_by("-created_at")


  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["run"] = self.run
      context["viewing_current_run"] = self.viewing_current_run
      context["other_runs_to_show"] = []
      run_count = Run.objects.count()
      show_other_runs = (
        (self.viewing_current_run and run_count > 1) or
        (self.viewing_current_run and run_count == 1 and self.run is None)
      )
      if show_other_runs:
        context["other_runs_to_show"] = list(Run.objects.order_by("-created_at"))
        if self.run is not None:
          context["other_runs_to_show"] = [run for run in context["other_runs_to_show"] if run.name != self.run.name]
      return context


class GamesListView(ListView):
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
      return context

    # paginator = Paginator(games, 100)
    # page_obj = paginator.get_page(self.kwargs["page"])
    # return
    # return render(request, 'list.html', {'page_obj': page_obj})

    # # We're returning the networks, because we display games organized by network
    # return Game.objects.filter(run=self.run).order_by("-created_at")