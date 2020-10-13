import pytest
from django.conf import settings
from django.test import RequestFactory

from src.apps.users.views import UserRedirectView, UserUpdateView

pytestmark = pytest.mark.django_db


# class TestUserUpdateView:
#     """
#     TODO:
#         extracting view initialization code as class-scoped fixture
#         would be great if only pytest-django supported non-function-scoped
#         fixture db access -- this is a work-in-progress for now:
#         https://github.com/pytest-dev/pytest-django/pull/258
#     """

#     def test_get_success_url(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
#         view = UserUpdateView()
#         request = request_factory.get("/fake-url/")
#         request.user = user

#         view.request = request

#         assert view.get_success_url() == f"/users/{user.username}/"

#     def test_get_object(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
#         view = UserUpdateView()
#         request = request_factory.get("/fake-url/")
#         request.user = user

#         view.request = request

#         assert view.get_object() == user


# class TestUserRedirectView:
#     def test_get_redirect_url(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
#         view = UserRedirectView()
#         request = request_factory.get("/fake-url")
#         request.user = user

#         view.request = request

#         assert view.get_redirect_url() == f"/users/{user.username}/"
