import copy

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from src.apps.runs.models import Run
from src.apps.trainings.models import Network

pytestmark = pytest.mark.django_db

User = get_user_model()

fake_sha256 = "12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd"


class TestGetStrongestNetwork:
    def setup_method(self):
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            log_gamma_uncertainty=0.02,
            log_gamma_lower_confidence=0 - 2 * 0.02,
            is_random=True,
            training_games_enabled=True,
        )
        self.n2 = Network.objects.create(
            run=self.r1,
            name="net-1",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=35,
            log_gamma_uncertainty=0.05,
            log_gamma_lower_confidence=35 - 2 * 0.05,
            training_games_enabled=True,
        )
        self.n3 = Network.objects.create(
            run=self.r1,
            name="net-3",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=45,
            log_gamma_uncertainty=0.07,
            log_gamma_lower_confidence=45 - 2 * 0.07,
            training_games_enabled=True,
        )
        self.n4 = Network.objects.create(
            run=self.r1,
            name="net-4",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=60,
            log_gamma_uncertainty=0.77,
            log_gamma_lower_confidence=60 - 2 * 0.77,
            training_games_enabled=True,
        )
        self.n5 = Network.objects.create(
            run=self.r1,
            name="net-5",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=45.1,
            log_gamma_uncertainty=0.45,
            log_gamma_lower_confidence=45.1 - 2 * 0.45,
            training_games_enabled=True,
        )

    def teardown_method(self):
        self.n5.delete()
        self.n4.delete()
        self.n3.delete()
        self.n2.delete()
        self.n1.delete()
        self.r1.delete()

    def test_get_strongest_network_anonymous(self):
        client = APIClient()
        response = client.get("/api/networks/get_strongest/", {})
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        data["run"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/net-3/', 'run': None, 'name': 'net-3', 'created_at': None, 'is_random': False, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}"""
        )
        assert response.status_code == 200


class TestGetStrongestNetworkNoSuitableNetwork:
    def setup_method(self):
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            log_gamma_uncertainty=0.02,
            log_gamma_lower_confidence=0 - 2 * 0.02,
            is_random=True,
            training_games_enabled=False,
        )

    def teardown_method(self):
        self.n1.delete()
        self.r1.delete()

    def test_get_strongest_network_anonymous(self):
        client = APIClient()
        response = client.get("/api/networks/get_strongest/", {})
        data = copy.deepcopy(response.data)
        assert str(data) == """{'error': 'No networks found for run enabled for training games.'}"""
        assert response.status_code == 400


class TestGetStrongestNetworkNoRun:
    def test_get_strongest_network_anonymous(self):
        client = APIClient()
        response = client.get("/api/networks/get_strongest/", {})
        data = copy.deepcopy(response.data)
        assert str(data) == """{'error': 'No active run.'}"""
        assert response.status_code == 404
