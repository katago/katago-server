from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from katago_server.games.api import GameViewSet
from katago_server.trainings.api import NetworkViewSet
from katago_server.users.api import GroupViewSet, UserViewSet

from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from allauth.account.models import EmailAddress
from django.contrib.sites.models import Site
from django_celery_beat.models import SolarSchedule, CrontabSchedule, ClockedSchedule, IntervalSchedule, PeriodicTask

admin.site.unregister(Group)
admin.site.unregister(Token)
admin.site.unregister(EmailAddress)
admin.site.unregister(Site)
admin.site.unregister(SolarSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)
router.register(r"networks", NetworkViewSet)
router.register(r"games", GameViewSet)

# API
api_urlpattern = [
    path("api/", include(router.urls)),
    path('api/token', obtain_auth_token, name='api_token_auth')
]

urlpatterns = (
    api_urlpattern
    + [
        path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
        path(
            "about/",
            TemplateView.as_view(template_name="pages/about.html"),
            name="about",
        ),
        # Django Admin, use {% url 'admin:index' %}
        path(settings.ADMIN_URL, admin.site.urls),
        path(f'{settings.ADMIN_URL}doc/', include('django.contrib.admindocs.urls')),
        # User management
        path("users/", include("katago_server.users.urls", namespace="users")),
        path("accounts/", include("allauth.urls")),
        # Your stuff: custom urls includes go here
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
