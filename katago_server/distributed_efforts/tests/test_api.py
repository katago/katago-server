import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from katago_server.runs.models import Run
from katago_server.trainings.models import Network

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestAPI:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(name="test-run", rating_game_probability=0.0, status="Active")
        self.n1 = Network.objects.create(run=self.r1, name="123456", model_file="123456.gz", log_gamma=2)

    def teardown_method(self):
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_job_anonymous(self):
        """
        An anonymous user should connect to get a new task
        """
        # Given
        client = APIClient()
        # When
        response = client.post("/api/tasks/", {})
        # Then
        assert response.status_code == 401
        assert response.data["detail"] == "Authentication credentials were not provided."

    def test_get_job_authenticated(self):
        # Given
        client = APIClient()
        client.login(username="test", password="test")
        # When
        response = client.post("/api/tasks/", {})
        # Then
        assert response.status_code == 200
        assert response.data["config"] == "FILL ME"
        assert response.data["kind"] == "selfplay"
        assert response.data["network"] == {
            "is_random": False,
            "model_file_bytes": 0,
            "model_file_sha256": "",
            "name": "123456",
            "model_file": "http://testserver/media/123456.gz",
        }
