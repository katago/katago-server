import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestAPI:
    def setup_method(self):
        self.u1 = User.objects.create_user(username='test', password='katago123')

    def test_get_job(self):
        # A user with proto_user params does not exist yet.
        client = APIClient()
        client.login(username='test', password='katago123')
        request = client.post('/api/tasks/get_job/', {})

        assert request.status_code == 200


