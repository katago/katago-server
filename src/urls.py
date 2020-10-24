from django.conf import settings
from django.conf.urls import url
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from rest_framework import routers, permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from src.apps.distributed_efforts.viewsets import DistributedTaskViewSet
from src.apps.games.viewsets import TrainingGameViewSet, RatingGameViewSet
from src.apps.runs.viewsets import RunViewSet
from src.apps.trainings.viewsets import NetworkViewSet
from src.apps.users.viewsets import UserViewSet
from src.apps.startposes.viewsets import StartPosViewSet

from src.frontend.views import (
    NetworksView,
    ContributionsView,
    GameNetworkGroupsView,
    GamesListByNetworkView,
    GamesListByUserView,
    SgfDetailView
)

from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from allauth.account.models import EmailAddress
from django.contrib.sites.models import Site
from django_celery_beat.models import SolarSchedule, CrontabSchedule, ClockedSchedule

admin.site.unregister(Group)
admin.site.unregister(Token)
admin.site.unregister(EmailAddress)
admin.site.unregister(Site)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"networks", NetworkViewSet)
router.register(r"startposes", StartPosViewSet)
router.register(r"games/training", TrainingGameViewSet)
router.register(r"games/rating", RatingGameViewSet)
router.register(r"runs", RunViewSet)
router.register(r"tasks", DistributedTaskViewSet, basename="Task")


# API
api_url_pattern = [path("api/", include(router.urls))]

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
api_swagger = [
    url(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json",),
    url(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui",),
    url(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

urlpatterns = (
    api_url_pattern
    + [
        path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
        # Django Admin, use {% url 'admin:index' %}
        path(settings.ADMIN_URL, admin.site.urls),
        path(f"{settings.ADMIN_URL}doc/", include("django.contrib.admindocs.urls")),
        path("accounts/", include("allauth.urls")),

        # Networks ------------------------------------------------------------
        path(
            "networks/",
            NetworksView.as_view(),
            {"run": None},
            name="current_run_networks"
        ),
        path(
            "networks/<run>/",
            NetworksView.as_view(), name="networks"
        ),

        # Games ---------------------------------------------------------------
        path(
            "games/",
            GameNetworkGroupsView.as_view(),
            {"run": None},
            name="current_run_game_network_groups"
        ),
        path(
            "games/<run>/",
            GameNetworkGroupsView.as_view(),
            name="game_network_groups"
        ),
        path(
            "contributions/",
            ContributionsView.as_view(),
            {"run": None},
            name="contributions"
        ),

        # **********************************************************
        # NOTE: if editing the below, make sure to keep them in sync with
        # src/templatehelpers/templatetags/custom_url_tags.py
        # **********************************************************

        path(
            "networks/<run>/<network>/training-games/",
            GamesListByNetworkView.as_view(),
            {"kind": "training"},
            name="training_games_list_by_network"
        ),
        path(
            "networks/<run>/<network>/rating-games/",
            GamesListByNetworkView.as_view(),
            {"kind": "rating"},
            name="rating_games_list_by_network"
        ),
        path(
            "contributions/<user>/training-games/",
            GamesListByUserView.as_view(),
            {"kind": "training"},
            name="training_games_list_by_user"
        ),
        path(
            "contributions/<user>/rating-games/",
            GamesListByUserView.as_view(),
            {"kind": "rating"},
            name="rating_games_list_by_user"
        ),
        path(
            "sgfplayer/training-games/<id>/",
            SgfDetailView.as_view(),
            {"kind": "training"},
            name="sgfplayer_training"
        ),
        path(
            "sgfplayer/rating-games/<id>/",
            SgfDetailView.as_view(),
            {"kind": "rating"},
            name="sgfplayer_rating"
        ),

    ]
    + api_swagger
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")},),
        path("403/", default_views.permission_denied, kwargs={"exception": Exception("Permission Denied")},),
        path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page not Found")},),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
