from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from rest_framework import routers

from src.apps.distributed_efforts.viewsets import DistributedTaskViewSet
from src.apps.games.viewsets import RatingGameViewSet, TrainingGameViewSet
from src.apps.runs.viewsets import RunViewSet
from src.apps.startposes.viewsets import StartPosViewSet
from src.apps.trainings.viewsets import NetworkViewSet, NetworkViewSetForElo
from src.apps.users.viewsets import UserViewSet
from src.frontend.views import (
    AccountView,
    ContributionsByRunView,
    ContributionsView,
    GameNetworkGroupsView,
    GamesListByNetworkView,
    GamesListByUserView,
    HomeView,
    NetworksView,
    RunInfoView,
    RunsListView,
    SgfDetailView,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"networks", NetworkViewSet)
router.register(r"networks-for-elo", NetworkViewSetForElo, basename="networks-for-elo")
router.register(r"startposes", StartPosViewSet)
router.register(r"games/training", TrainingGameViewSet)
router.register(r"games/rating", RatingGameViewSet)
router.register(r"runs", RunViewSet)
router.register(r"tasks", DistributedTaskViewSet, basename="Task")


# API
api_url_pattern = [path("api/", include(router.urls))]


urlpatterns = (
    api_url_pattern
    + [
        path("", HomeView.as_view(), name="home"),
        # Django Admin, use {% url 'admin:index' %}
        path(settings.ADMIN_URL, admin.site.urls),
        path(f"{settings.ADMIN_URL}doc/", include("django.contrib.admindocs.urls")),
        path("account/", AccountView.as_view(), name="account_page"),
        path("accounts/", include("allauth.urls")),
        # Health check
        path("healthz/", include("health_check.urls")),
        # Runs ------------------------------------------------------------
        path("runs/", RunsListView.as_view(), name="runs"),
        path("runs/<run>/", RunInfoView.as_view(), name="run_info"),
        # Networks ------------------------------------------------------------
        path(
            "networks/",
            NetworksView.as_view(),
            {"run": None},
            name="current_run_networks",
        ),
        path("networks/<run>/", NetworksView.as_view(), name="networks"),
        # Games ---------------------------------------------------------------
        path(
            "games/",
            GameNetworkGroupsView.as_view(),
            {"run": None},
            name="current_run_game_network_groups",
        ),
        path("games/<run>/", GameNetworkGroupsView.as_view(), name="game_network_groups"),
        # Contributions ---------------------------------------------------------------
        path("contributions/", ContributionsView.as_view(), name="overall_contributions"),
        path(
            "contributions/<run>/",
            ContributionsByRunView.as_view(),
            name="contributions",
        ),
        # **********************************************************
        # NOTE: if editing the below, make sure to keep them in sync with
        # src/templatehelpers/templatetags/custom_url_tags.py
        # **********************************************************
        path(
            "networks/<run>/<network>/training-games/",
            GamesListByNetworkView.as_view(),
            {"kind": "training"},
            name="training_games_list_by_network",
        ),
        path(
            "networks/<run>/<network>/rating-games/",
            GamesListByNetworkView.as_view(),
            {"kind": "rating"},
            name="rating_games_list_by_network",
        ),
        path(
            "contributions/<user>/training-games/",
            GamesListByUserView.as_view(),
            {"kind": "training"},
            name="training_games_list_by_user",
        ),
        path(
            "contributions/<user>/rating-games/",
            GamesListByUserView.as_view(),
            {"kind": "rating"},
            name="rating_games_list_by_user",
        ),
        path(
            "sgfplayer/training-games/<id>/",
            SgfDetailView.as_view(),
            {"kind": "training"},
            name="sgfplayer_training",
        ),
        path(
            "sgfplayer/rating-games/<id>/",
            SgfDetailView.as_view(),
            {"kind": "rating"},
            name="sgfplayer_rating",
        ),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
