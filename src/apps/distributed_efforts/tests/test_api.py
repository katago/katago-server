import base64
import copy
import random

import numpy as np
import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient

from src.apps.distributed_efforts.models import UserLastVersion
from src.apps.runs.models import Run
from src.apps.startposes.models import StartPos
from src.apps.startposes.tasks import recompute_startpos_cumulative_weights
from src.apps.trainings.models import Network

pytestmark = pytest.mark.django_db

User = get_user_model()

fake_sha256 = "12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd"


class TestGetSelfplayTask:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
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
            is_random=True,
        )

    def teardown_method(self):
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_job_anonymous(self):
        """
        An anonymous user should connect to get a new task
        """
        client = APIClient()
        response = client.post("/api/tasks/", {})
        assert response.status_code == 401
        assert (
            str(response.data)
            == """{'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')}"""
        )
        response = client.post("/api/tasks/", {"git_revision": "abcdef123456abcdef123456abcdef1234567890"})
        assert response.status_code == 401
        assert (
            str(response.data)
            == """{'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')}"""
        )

    def test_get_job_authenticated_no_git_revision(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {})
        assert response.status_code == 400
        assert (
            str(response.data)
            == """{'error': "This version of KataGo is not usable for distributed because either it's had custom modifications or has been compiled without version info."}"""
        )

    def test_get_job_authenticated_blank_git_revision(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision": ""})
        assert response.status_code == 400
        assert (
            str(response.data)
            == """{'error': "This version of KataGo is not usable for distributed because either it's had custom modifications or has been compiled without version info."}"""
        )

    def test_get_job_authenticated_short_git_revision(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision": "abcd"})
        assert response.status_code == 400
        assert (
            str(response.data)
            == """{'error': "This version of KataGo is not usable for distributed because either it's had custom modifications or has been compiled without version info."}"""
        )

    def test_get_job_authenticated_bad_git_revision(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision": "0000111122223333444455556666777788889999"})
        assert response.status_code == 400
        assert (
            str(response.data)
            == """{'error': 'This version of KataGo is not enabled for distributed. If this exact version was working previously, then changes in the run require a newer version - please update KataGo to the latest version or release. But if this is already the official newest version of KataGo, or you think that not enabling this version is an oversight, please ask server admins to enable the following version hash: 0000111122223333444455556666777788889999'}"""
        )

    def test_get_job_authenticated_valid_git_revision1(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision": "abcdef123456abcdef123456abcdef1234567890"})
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
        )
        assert response.status_code == 200

    def test_get_job_authenticated_valid_git_revision1_multipart(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post(
            "/api/tasks/",
            {"git_revision": "abcdef123456abcdef123456abcdef1234567890"},
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
        )
        assert response.status_code == 200

    def test_get_job_authenticated_valid_git_revision2(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision": "1111222233334444555566667777888899990000"})
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
        )
        assert response.status_code == 200
        assert (
            UserLastVersion.objects.filter(user__username="test").first().git_revision
            == "1111222233334444555566667777888899990000"
        )

    def test_get_job_no_trailing_slash(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks", {"git_revision": "1111222233334444555566667777888899990000"})
        assert response.url == "/api/tasks/"
        assert response.status_code == 301


class TestGetRatingTask:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=1.0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-network0",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            log_gamma_uncertainty=1,
            log_gamma_lower_confidence=-2.0,
            log_gamma_upper_confidence=2.0,
            log_gamma_game_count=3,
            is_random=True,
        )
        self.n2 = Network.objects.create(
            run=self.r1,
            name="testrun-network1",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=1,
            log_gamma_uncertainty=1.5,
            log_gamma_lower_confidence=-3.0,
            log_gamma_upper_confidence=4.0,
            log_gamma_game_count=5,
            is_random=True,
        )

    def teardown_method(self):
        self.n2.delete()
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_job_authenticated_valid_git_revision2(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision": "1111222233334444555566667777888899990000"})
        data = copy.deepcopy(response.data)
        data["white_network"]["created_at"] = None  # Suppress timestamp for test
        data["black_network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'rating', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'white_network': {'url': 'http://testserver/api/networks/testrun-network0/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network0', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'black_network': {'url': 'http://testserver/api/networks/testrun-network1/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network1', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}}"""
            or str(data)
            == """{'kind': 'rating', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'white_network': {'url': 'http://testserver/api/networks/testrun-network1/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network1', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'black_network': {'url': 'http://testserver/api/networks/testrun-network0/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network0', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}}"""
        )
        assert response.status_code == 200


class TestGetSelfplayTaskForced:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=1.0,
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
            is_random=True,
        )
        self.n2 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork2",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
            training_games_enabled=False,
        )

    def teardown_method(self):
        self.n2.delete()
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_job_fail(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.rating_game_probability = 1.0
        self.r1.save()
        response = client.post(
            "/api/tasks/",
            {
                "git_revision": "abcdef123456abcdef123456abcdef1234567890",
                "allow_rating_task": False,
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        assert (
            str(data)
            == """{'error': 'allow_rating_task is false but this server is only serving rating games right now'}"""
        )
        assert response.status_code == 400

    def test_get_job_success(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.rating_game_probability = 0.999999999999
        self.r1.save()
        response = client.post(
            "/api/tasks/",
            {
                "git_revision": "abcdef123456abcdef123456abcdef1234567890",
                "allow_rating_task": False,
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
        )
        assert response.status_code == 200


class TestGetRatingTaskForced:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-network0",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            log_gamma_uncertainty=1,
            log_gamma_lower_confidence=-2.0,
            log_gamma_upper_confidence=2.0,
            is_random=True,
        )
        self.n2 = Network.objects.create(
            run=self.r1,
            name="testrun-network1",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=1,
            log_gamma_uncertainty=1.5,
            log_gamma_lower_confidence=-3.0,
            log_gamma_upper_confidence=4.0,
            is_random=True,
        )

    def teardown_method(self):
        self.n2.delete()
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_job_fail(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.rating_game_probability = 0
        self.r1.save()
        response = client.post(
            "/api/tasks/",
            {
                "git_revision": "1111222233334444555566667777888899990000",
                "allow_selfplay_task": False,
            },
        )
        data = copy.deepcopy(response.data)
        assert (
            str(data)
            == """{'error': 'allow_selfplay_task is false but this server is only serving selfplay games right now'}"""
        )
        assert response.status_code == 400

    def test_get_job_success(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.rating_game_probability = 0.0000001
        self.r1.save()
        response = client.post(
            "/api/tasks/",
            {
                "git_revision": "1111222233334444555566667777888899990000",
                "allow_selfplay_task": False,
            },
        )
        data = copy.deepcopy(response.data)
        data["white_network"]["created_at"] = None  # Suppress timestamp for test
        data["black_network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'rating', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'white_network': {'url': 'http://testserver/api/networks/testrun-network0/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network0', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'black_network': {'url': 'http://testserver/api/networks/testrun-network1/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network1', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}}"""
            or str(data)
            == """{'kind': 'rating', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'white_network': {'url': 'http://testserver/api/networks/testrun-network1/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network1', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'black_network': {'url': 'http://testserver/api/networks/testrun-network0/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network0', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}}"""
        )
        assert response.status_code == 200


class TestUncertaintyVsEloVsData:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=1,
            rating_game_variability_scale=1.0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )
        self.n1a = Network.objects.create(
            run=self.r1,
            name="1a",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=100.0003,
            log_gamma_uncertainty=1.0003,
            log_gamma_lower_confidence=98.0003,
            log_gamma_upper_confidence=102.0003,
            log_gamma_game_count=10001,
            is_random=True,
        )
        self.n1b = Network.objects.create(
            run=self.r1,
            name="1b",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=100.0002,
            log_gamma_uncertainty=1.0002,
            log_gamma_lower_confidence=98.0002,
            log_gamma_upper_confidence=102.0002,
            log_gamma_game_count=10002,
            is_random=True,
        )
        self.n1c = Network.objects.create(
            run=self.r1,
            name="1c",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=100.0001,
            log_gamma_uncertainty=1.0001,
            log_gamma_lower_confidence=98.0001,
            log_gamma_upper_confidence=102.0001,
            log_gamma_game_count=10003,
            is_random=True,
        )
        self.n2a = Network.objects.create(
            run=self.r1,
            name="2a",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=50.0003,
            log_gamma_uncertainty=10.0003,
            log_gamma_lower_confidence=30.0003,
            log_gamma_upper_confidence=70.0003,
            log_gamma_game_count=10004,
            is_random=True,
        )
        self.n2b = Network.objects.create(
            run=self.r1,
            name="2b",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=50.0002,
            log_gamma_uncertainty=10.0002,
            log_gamma_lower_confidence=30.0002,
            log_gamma_upper_confidence=70.0002,
            log_gamma_game_count=10005,
            is_random=True,
        )
        self.n2c = Network.objects.create(
            run=self.r1,
            name="2c",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=50.0001,
            log_gamma_uncertainty=10.0001,
            log_gamma_lower_confidence=30.0001,
            log_gamma_upper_confidence=70.0001,
            log_gamma_game_count=10006,
            is_random=True,
        )
        self.n3a = Network.objects.create(
            run=self.r1,
            name="3a",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=20.0003,
            log_gamma_uncertainty=2.0003,
            log_gamma_lower_confidence=18.0003,
            log_gamma_upper_confidence=22.0003,
            log_gamma_game_count=1001,
            is_random=True,
        )
        self.n3b = Network.objects.create(
            run=self.r1,
            name="3b",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=20.0002,
            log_gamma_uncertainty=2.0002,
            log_gamma_lower_confidence=18.0002,
            log_gamma_upper_confidence=22.0002,
            log_gamma_game_count=1002,
            is_random=True,
        )
        self.n3c = Network.objects.create(
            run=self.r1,
            name="3c",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=20.0001,
            log_gamma_uncertainty=2.0001,
            log_gamma_lower_confidence=18.0001,
            log_gamma_upper_confidence=22.0001,
            log_gamma_game_count=1003,
            is_random=True,
        )

    def teardown_method(self):
        self.n1a.delete()
        self.n1b.delete()
        self.n1c.delete()
        self.n2a.delete()
        self.n2b.delete()
        self.n2c.delete()
        self.n3a.delete()
        self.n3b.delete()
        self.n3c.delete()
        self.r1.delete()
        self.u1.delete()

    def test_high_elo(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.rating_game_high_elo_probability = 1000
        self.r1.rating_game_high_uncertainty_probability = 0
        self.r1.rating_game_low_data_probability = 0
        self.r1.save()

        random.seed(12345)
        np.random.seed(23456)
        counts = {}
        for i in range(100):
            response = client.post(
                "/api/tasks/",
                {"git_revision": "1111222233334444555566667777888899990000"},
            )
            name = response.data["white_network"]["name"]
            if name not in counts:
                counts[name] = 0
            counts[name] += 1
            name = response.data["black_network"]["name"]
            if name not in counts:
                counts[name] = 0
            counts[name] += 1
        s = ""
        for k, v in sorted(counts.items()):
            s += k + ":" + str(v) + ", "
        assert s == "1a:51, 1b:53, 1c:38, 2a:20, 2b:16, 2c:8, 3a:7, 3b:6, 3c:1, "

    def test_high_uncertainty(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.rating_game_high_elo_probability = 0
        self.r1.rating_game_high_uncertainty_probability = 1000
        self.r1.rating_game_low_data_probability = 0
        self.r1.save()

        random.seed(12345)
        np.random.seed(23456)
        counts = {}
        for i in range(100):
            response = client.post(
                "/api/tasks/",
                {"git_revision": "1111222233334444555566667777888899990000"},
            )
            name = response.data["white_network"]["name"]
            if name not in counts:
                counts[name] = 0
            counts[name] += 1
            name = response.data["black_network"]["name"]
            if name not in counts:
                counts[name] = 0
            counts[name] += 1
        s = ""
        for k, v in sorted(counts.items()):
            s += k + ":" + str(v) + ", "
        assert s == "1a:4, 1b:18, 1c:11, 2a:46, 2b:48, 2c:28, 3a:21, 3b:16, 3c:8, "

    def test_low_data(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.rating_game_high_elo_probability = 0
        self.r1.rating_game_high_uncertainty_probability = 0
        self.r1.rating_game_low_data_probability = 1000
        self.r1.save()

        random.seed(12345)
        np.random.seed(23456)
        counts = {}
        for i in range(100):
            response = client.post(
                "/api/tasks/",
                {"git_revision": "1111222233334444555566667777888899990000"},
            )
            name = response.data["white_network"]["name"]
            if name not in counts:
                counts[name] = 0
            counts[name] += 1
            name = response.data["black_network"]["name"]
            if name not in counts:
                counts[name] = 0
            counts[name] += 1
        s = ""
        for k, v in sorted(counts.items()):
            s += k + ":" + str(v) + ", "
        assert s == "1a:14, 1b:11, 1c:13, 2a:5, 2b:17, 2c:11, 3a:50, 3b:47, 3c:32, "

    def test_mix(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.rating_game_high_elo_probability = 1000
        self.r1.rating_game_high_uncertainty_probability = 1000
        self.r1.rating_game_low_data_probability = 1000
        self.r1.save()

        random.seed(12345)
        np.random.seed(23456)
        counts = {}
        for i in range(100):
            response = client.post(
                "/api/tasks/",
                {"git_revision": "1111222233334444555566667777888899990000"},
            )
            name = response.data["white_network"]["name"]
            if name not in counts:
                counts[name] = 0
            counts[name] += 1
            name = response.data["black_network"]["name"]
            if name not in counts:
                counts[name] = 0
            counts[name] += 1
        s = ""
        for k, v in sorted(counts.items()):
            s += k + ":" + str(v) + ", "
        assert s == "1a:27, 1b:31, 1c:15, 2a:20, 2b:28, 2c:15, 3a:26, 3b:23, 3c:15, "


class TestExtremeEloStability:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=1,
            rating_game_low_data_probability=1.0,
            rating_game_high_uncertainty_probability=0.0,
            rating_game_high_elo_probability=0.0,
            rating_game_variability_scale=0.01,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )
        self.n1a = Network.objects.create(
            run=self.r1,
            name="1a",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=5,
            log_gamma_uncertainty=1,
            log_gamma_game_count=0,
            is_random=True,
        )
        self.n1b = Network.objects.create(
            run=self.r1,
            name="1b",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=7,
            log_gamma_uncertainty=1,
            log_gamma_game_count=1,
            is_random=True,
        )
        self.n1c = Network.objects.create(
            run=self.r1,
            name="1c",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=8,
            log_gamma_uncertainty=1,
            log_gamma_game_count=2,
            is_random=True,
        )
        self.n1d = Network.objects.create(
            run=self.r1,
            name="1d",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=10,
            log_gamma_uncertainty=1,
            log_gamma_game_count=3,
            is_random=True,
        )
        self.n1e = Network.objects.create(
            run=self.r1,
            name="1e",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=11,
            log_gamma_uncertainty=1,
            log_gamma_game_count=4,
            is_random=True,
        )

    def teardown_method(self):
        self.n1a.delete()
        self.n1b.delete()
        self.n1c.delete()
        self.n1d.delete()
        self.n1e.delete()
        self.r1.delete()
        self.u1.delete()

    def test_stability(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.save()

        random.seed(12345)
        np.random.seed(23456)
        counts = {}
        for i in range(100):
            response = client.post(
                "/api/tasks/",
                {"git_revision": "1111222233334444555566667777888899990000"},
            )
            names = response.data["white_network"]["name"] + response.data["black_network"]["name"]
            if names not in counts:
                counts[names] = 0
            counts[names] += 1
        s = ""
        for k, v in sorted(counts.items()):
            s += k + ":" + str(v) + ", "
        assert s == "1a1b:21, 1b1a:16, 1b1c:19, 1c1b:25, 1d1e:9, 1e1d:10, "


class TestGetTaskNoNetwork:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )

    def teardown_method(self):
        self.r1.delete()
        self.u1.delete()

    def test_get_job_authenticated_valid_git_revision1(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision": "abcdef123456abcdef123456abcdef1234567890"})
        data = copy.deepcopy(response.data)
        assert str(data) == """{'error': 'No networks found for run enabled for training games.'}"""
        assert response.status_code == 400


class TestGetTaskNoEnabledNetwork:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
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
            is_random=True,
            training_games_enabled=False,
        )

    def teardown_method(self):
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_job_authenticated_valid_git_revision1(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision": "abcdef123456abcdef123456abcdef1234567890"})
        data = copy.deepcopy(response.data)
        assert str(data) == """{'error': 'No networks found for run enabled for training games.'}"""
        assert response.status_code == 400


class TestPostNetwork:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="testadmin", password="testadmin", is_superuser=True, is_staff=True)
        self.u2 = User.objects.create_user(username="testplain", password="testplain")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )

    def teardown_method(self):
        Network.objects.filter(name="networkname7").delete()
        Network.objects.select_networks_for_run(self.r1).delete()
        self.r1.delete()
        self.u2.delete()
        self.u1.delete()

    def test_post_network_not_allowed(self):
        client = APIClient()
        client.login(username="testplain", password="testplain")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile("networkname.bin.gz", b"", content_type="application/octet-stream"),
                "model_file_bytes": "0",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        assert (
            str(data)
            == """{'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')}"""
        )
        assert response.status_code == 403

    def test_post_network_no_trailing_slash(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname2",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile("networkname2.bin.gz", b"", content_type="application/octet-stream"),
                "model_file_bytes": "0",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            },
            format="multipart",
        )
        assert response.url == "/api/networks/"
        assert response.status_code == 301

    def test_post_network_empty(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname2",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile("networkname2.bin.gz", b"", content_type="application/octet-stream"),
                "model_file_bytes": "0",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        assert str(data) == """{'model_file': [ErrorDetail(string='The submitted file is empty.', code='empty')]}"""
        assert response.status_code == 400

    def test_post_network_no_file_random(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networknamenofilerandom",
                "network_size": "random",
                "is_random": "true",
                "model_file_bytes": "0",
                "model_file_sha256": "-",
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/networknamenofilerandom/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networknamenofilerandom', 'created_at': None, 'network_size': 'random', 'is_random': True, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '-', 'model_zip_file': None, 'parent_network': None, 'train_step': None, 'total_num_data_rows': None, 'extra_stats': {}, 'notes': '', 'log_gamma': 0.0, 'log_gamma_uncertainty': 0.0, 'log_gamma_lower_confidence': 0.0, 'log_gamma_upper_confidence': 0.0, 'log_gamma_game_count': 0}"""
        )
        assert response.status_code == 201

    def test_post_network_no_file_nonrandom(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networknamenofilenonrandom",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file_bytes": "0",
                "model_file_sha256": "-",
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        assert (
            str(data)
            == """{'non_field_errors': [ErrorDetail(string='model_file is only allowed to be blank when is_random is True', code='invalid')]}"""
        )
        assert response.status_code == 400

    def test_post_network_not_a_zip(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname3",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile("networkname3.bin.gz", b"Hello world", content_type="text/plain"),
                "model_file_bytes": "1",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        assert (
            str(data)
            == """{'model_file': [ErrorDetail(string='Files of type text/plain are not supported.', code='content_type')]}"""
        )
        assert response.status_code == 400

    def test_post_network_gzip(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname4",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile(
                    "networkname4.bin.gz",
                    base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="),
                    content_type="application/gzip",
                ),
                "model_file_bytes": "28",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/networkname4/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname4', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/models/testrun/networkname4.bin.gz', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': None, 'train_step': None, 'total_num_data_rows': None, 'extra_stats': {}, 'notes': '', 'log_gamma': 0.0, 'log_gamma_uncertainty': 0.0, 'log_gamma_lower_confidence': 0.0, 'log_gamma_upper_confidence': 0.0, 'log_gamma_game_count': 0}"""
        )
        assert response.status_code == 201

    def test_post_network_loggamma_only(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname4b",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile(
                    "networkname4b.bin.gz",
                    base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="),
                    content_type="application/gzip",
                ),
                "model_file_bytes": "28",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
                "log_gamma": "4",
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/networkname4b/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname4b', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/models/testrun/networkname4b.bin.gz', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': None, 'train_step': None, 'total_num_data_rows': None, 'extra_stats': {}, 'notes': '', 'log_gamma': 4.0, 'log_gamma_uncertainty': 2.0, 'log_gamma_lower_confidence': 0.0, 'log_gamma_upper_confidence': 8.0, 'log_gamma_game_count': 0}"""
        )
        assert response.status_code == 201

    def test_post_network_loggamma_partial(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname5",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile(
                    "networkname5.bin.gz",
                    base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="),
                    content_type="application/gzip",
                ),
                "model_file_bytes": "28",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
                "log_gamma": "4",
                "log_gamma_uncertainty": "1.5",
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/networkname5/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname5', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/models/testrun/networkname5.bin.gz', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': None, 'train_step': None, 'total_num_data_rows': None, 'extra_stats': {}, 'notes': '', 'log_gamma': 4.0, 'log_gamma_uncertainty': 1.5, 'log_gamma_lower_confidence': 1.0, 'log_gamma_upper_confidence': 7.0, 'log_gamma_game_count': 0}"""
        )
        assert response.status_code == 201

    def test_post_network_loggamma_full(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname6",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile(
                    "networkname6.bin.gz",
                    base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="),
                    content_type="application/gzip",
                ),
                "model_file_bytes": "28",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
                "log_gamma": "4",
                "log_gamma_uncertainty": "2",
                "log_gamma_lower_confidence": "3",
                "log_gamma_upper_confidence": "7",
                "log_gamma_game_count": "12",
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/networkname6/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname6', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/models/testrun/networkname6.bin.gz', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': None, 'train_step': None, 'total_num_data_rows': None, 'extra_stats': {}, 'notes': '', 'log_gamma': 4.0, 'log_gamma_uncertainty': 2.0, 'log_gamma_lower_confidence': 3.0, 'log_gamma_upper_confidence': 7.0, 'log_gamma_game_count': 12}"""
        )
        assert response.status_code == 201

        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname7",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile(
                    "networkname7.bin.gz",
                    base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="),
                    content_type="application/gzip",
                ),
                "model_file_bytes": "28",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
                "parent_network": "http://testserver/api/networks/networkname6/",
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/networkname7/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname7', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/models/testrun/networkname7.bin.gz', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': 'http://testserver/api/networks/networkname6/', 'train_step': None, 'total_num_data_rows': None, 'extra_stats': {}, 'notes': '', 'log_gamma': 4.0, 'log_gamma_uncertainty': 2.0, 'log_gamma_lower_confidence': 0.0, 'log_gamma_upper_confidence': 8.0, 'log_gamma_game_count': 0}"""
        )
        assert response.status_code == 201

    def test_post_network_with_stats(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname8",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile(
                    "networkname6.bin.gz",
                    base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="),
                    content_type="application/gzip",
                ),
                "model_file_bytes": "28",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
                "train_step": 12345678901234,
                "total_num_data_rows": 5678901234567,
                "extra_stats": '{"policy_loss": 12.5}',
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/networkname8/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname8', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/models/testrun/networkname8.bin.gz', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': None, 'train_step': 12345678901234, 'total_num_data_rows': 5678901234567, 'extra_stats': {'policy_loss': 12.5}, 'notes': '', 'log_gamma': 0.0, 'log_gamma_uncertainty': 0.0, 'log_gamma_lower_confidence': 0.0, 'log_gamma_upper_confidence': 0.0, 'log_gamma_game_count': 0}"""
        )
        assert response.status_code == 201

    # Verifies that the uploaded filename is based on the network name, not the user's uploaded file name
    def test_post_network_filename_overriden(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname9",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile(
                    "foobar.bin.gz",
                    base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="),
                    content_type="application/gzip",
                ),
                "model_file_bytes": "28",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/networkname9/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname9', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/models/testrun/networkname9.bin.gz', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': None, 'train_step': None, 'total_num_data_rows': None, 'extra_stats': {}, 'notes': '', 'log_gamma': 0.0, 'log_gamma_uncertainty': 0.0, 'log_gamma_lower_confidence': 0.0, 'log_gamma_upper_confidence': 0.0, 'log_gamma_game_count': 0}"""
        )
        assert response.status_code == 201

    # Verifies that the uploaded filename does keep the user's filename extension
    def test_post_network_filename_txt_gz(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname10",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile(
                    "foobar.txt.gz",
                    base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="),
                    content_type="application/gzip",
                ),
                "model_file_bytes": "28",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/networkname10/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname10', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/models/testrun/networkname10.txt.gz', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': None, 'train_step': None, 'total_num_data_rows': None, 'extra_stats': {}, 'notes': '', 'log_gamma': 0.0, 'log_gamma_uncertainty': 0.0, 'log_gamma_lower_confidence': 0.0, 'log_gamma_upper_confidence': 0.0, 'log_gamma_game_count': 0}"""
        )
        assert response.status_code == 201

    # Verifies that the uploaded filename does keep the user's filename extension
    def test_post_network_filename_abcd(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post(
            "/api/networks/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "name": "networkname11",
                "network_size": "b4c32",
                "is_random": "false",
                "model_file": SimpleUploadedFile(
                    "foobar.abcd.efgh",
                    base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="),
                    content_type="application/gzip",
                ),
                "model_zip_file": SimpleUploadedFile(
                    "foobar.aaaa",
                    base64.decodebytes(b"UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA=="),
                    content_type="application/zip",
                ),
                "model_file_bytes": "28",
                "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/networkname11/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname11', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/models/testrun/networkname11.efgh', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': 'http://testserver/media/networks/zips/testrun/networkname11.aaaa', 'parent_network': None, 'train_step': None, 'total_num_data_rows': None, 'extra_stats': {}, 'notes': '', 'log_gamma': 0.0, 'log_gamma_uncertainty': 0.0, 'log_gamma_lower_confidence': 0.0, 'log_gamma_upper_confidence': 0.0, 'log_gamma_game_count': 0}"""
        )
        assert response.status_code == 201


class TestStartPoses:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test", is_staff=True)
        self.u2 = User.objects.create_user(username="test2", password="test2", is_staff=False)
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.9999,  # Only one network, so shouldn't matter
            selfplay_startpos_probability=1.0,
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
            is_random=True,
        )

    def teardown_method(self):
        StartPos.objects.filter(run=self.r1).delete()
        self.n1.delete()
        self.r1.delete()
        self.u2.delete()
        self.u1.delete()

    def test_upload_startpos_auth_fail(self):
        StartPos.objects.filter(run=self.r1).delete()
        client = APIClient()
        client.login(username="test2", password="test2")

        response = client.post(
            "/api/startposes/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "data": {"foo": 3, "bar": ["abc"]},
                "weight": 2.5,
            },
            format="json",
        )
        data = copy.deepcopy(response.data)
        assert (
            str(data)
            == """{'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')}"""
        )
        assert response.status_code == 403

    def test_upload_startpos_invalid(self):
        StartPos.objects.filter(run=self.r1).delete()
        client = APIClient()
        client.login(username="test", password="test")

        self.r1.startpos_locked = False
        self.r1.selfplay_startpos_probability = 1.0
        self.r1.save()
        response = client.post(
            "/api/startposes/",
            {"data": {"foo": 3, "bar": ["abc"]}, "weight": 2.5},
            format="json",
        )
        data = copy.deepcopy(response.data)
        assert str(data) == """{'run': [ErrorDetail(string='This field is required.', code='required')]}"""
        assert response.status_code == 400

    def test_upload_startpos_fail(self):
        StartPos.objects.filter(run=self.r1).delete()
        client = APIClient()
        client.login(username="test", password="test")

        self.r1.startpos_locked = False
        self.r1.selfplay_startpos_probability = 1.0
        self.r1.save()
        response = client.post(
            "/api/startposes/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "data": {"foo": 3, "bar": ["abc"]},
                "weight": 2.5,
            },
            format="json",
        )
        data = copy.deepcopy(response.data)
        assert (
            str(data)
            == """{'non_field_errors': [ErrorDetail(string='Can only upload while run startPoses are locked to prevent startpos races from clients.', code='invalid')]}"""
        )
        assert response.status_code == 400

    def test_upload_startpos_success_but_no_game(self):
        StartPos.objects.filter(run=self.r1).delete()
        client = APIClient()
        client.login(username="test", password="test")

        self.r1.startpos_locked = True
        self.r1.selfplay_startpos_probability = 1.0
        self.r1.save()
        response = client.post(
            "/api/startposes/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "data": {"foo": 3, "bar": ["abc"]},
                "weight": 2.5,
            },
            format="json",
        )
        data = copy.deepcopy(response.data)
        assert data["url"].startswith("http://testserver/api/startposes/")
        data["url"] = None  # Suppress url for test
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': None, 'run': 'http://testserver/api/runs/testrun/', 'created_at': None, 'weight': 2.5, 'data': {'foo': 3, 'bar': ['abc']}, 'notes': ''}"""
        )
        assert response.status_code == 201

        response = client.post(
            "/api/tasks/",
            {"git_revision": "abcdef123456abcdef123456abcdef1234567890"},
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
        )
        assert response.status_code == 200

    def test_upload_startpos_success_but_still_no_game(self):
        StartPos.objects.filter(run=self.r1).delete()
        client = APIClient()
        client.login(username="test", password="test")

        self.r1.startpos_locked = True
        self.r1.selfplay_startpos_probability = 1.0
        self.r1.save()
        response = client.post(
            "/api/startposes/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "data": {"foo": 3, "bar": ["abc"]},
                "weight": 2.5,
            },
            format="json",
        )
        data = copy.deepcopy(response.data)
        assert data["url"].startswith("http://testserver/api/startposes/")
        data["url"] = None  # Suppress url for test
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': None, 'run': 'http://testserver/api/runs/testrun/', 'created_at': None, 'weight': 2.5, 'data': {'foo': 3, 'bar': ['abc']}, 'notes': ''}"""
        )
        assert response.status_code == 201

        assert StartPos.objects.filter(run=self.r1).first().cumulative_weight == -1.0

        self.r1.startpos_locked = False
        self.r1.selfplay_startpos_probability = 1.0
        self.r1.save()
        response = client.post(
            "/api/tasks/",
            {"git_revision": "abcdef123456abcdef123456abcdef1234567890"},
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
        )
        assert response.status_code == 200

    def test_upload_startpos_success_but_still_no_game2(self):
        StartPos.objects.filter(run=self.r1).delete()
        client = APIClient()
        client.login(username="test", password="test")

        self.r1.startpos_locked = True
        self.r1.selfplay_startpos_probability = 1.0
        self.r1.save()
        response = client.post(
            "/api/startposes/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "data": {"foo": 3, "bar": ["abc"]},
                "weight": 2.5,
            },
            format="json",
        )
        data = copy.deepcopy(response.data)
        assert data["url"].startswith("http://testserver/api/startposes/")
        data["url"] = None  # Suppress url for test
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': None, 'run': 'http://testserver/api/runs/testrun/', 'created_at': None, 'weight': 2.5, 'data': {'foo': 3, 'bar': ['abc']}, 'notes': ''}"""
        )
        assert response.status_code == 201

        response = client.post(
            "/api/startposes/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "data": {"baz": 3, "123": [[(1, 2)]]},
                "weight": 4.0,
            },
            format="json",
        )

        recompute_startpos_cumulative_weights()

        assert StartPos.objects.filter(run=self.r1).order_by("id").first().cumulative_weight == 2.5
        assert StartPos.objects.filter(run=self.r1).order_by("-id").first().cumulative_weight == 6.5
        self.r1.refresh_from_db()
        assert self.r1.startpos_total_weight == 6.5

        response = client.post(
            "/api/tasks/",
            {"git_revision": "abcdef123456abcdef123456abcdef1234567890"},
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
        )

        assert response.status_code == 200

    def test_upload_startpos_success_with_game(self):
        StartPos.objects.filter(run=self.r1).delete()
        client = APIClient()
        client.login(username="test", password="test")

        self.r1.startpos_locked = True
        self.r1.selfplay_startpos_probability = 1.0
        self.r1.save()
        response = client.post(
            "/api/startposes/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "data": {"foo": 3, "bar": ["abc"]},
                "weight": 2.5,
            },
            format="json",
        )
        data = copy.deepcopy(response.data)
        assert data["url"].startswith("http://testserver/api/startposes/")
        data["url"] = None  # Suppress url for test
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': None, 'run': 'http://testserver/api/runs/testrun/', 'created_at': None, 'weight': 2.5, 'data': {'foo': 3, 'bar': ['abc']}, 'notes': ''}"""
        )
        assert response.status_code == 201

        response = client.post(
            "/api/startposes/",
            {
                "run": "http://testserver/api/runs/testrun/",
                "data": {"baz": 3, "123": [[(1, 2)]]},
                "weight": 4.0,
            },
            format="json",
        )

        recompute_startpos_cumulative_weights()

        self.r1.refresh_from_db()
        self.r1.startpos_locked = False
        self.r1.save()
        response = client.post(
            "/api/tasks/",
            {"git_revision": "abcdef123456abcdef123456abcdef1234567890"},
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': [{'bar': ['abc'], 'foo': 3}]}"""
            or str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': [{'123': [[[1, 2]]], 'baz': 3}]}"""
        )
        assert response.status_code == 200

    def test_startpos_distribution(self):
        StartPos.objects.filter(run=self.r1).delete()
        client = APIClient()
        client.login(username="test", password="test")

        self.r1.startpos_locked = True
        self.r1.selfplay_startpos_probability = 0.5
        self.r1.save()
        response = client.post(
            "/api/startposes/",
            {"run": "http://testserver/api/runs/testrun/", "data": "a", "weight": 5.0},
            format="json",
        )
        assert response.status_code == 201
        response = client.post(
            "/api/startposes/",
            {"run": "http://testserver/api/runs/testrun/", "data": "b", "weight": 2.0},
            format="json",
        )
        assert response.status_code == 201
        response = client.post(
            "/api/startposes/",
            {"run": "http://testserver/api/runs/testrun/", "data": "c", "weight": 10.0},
            format="json",
        )
        assert response.status_code == 201
        response = client.post(
            "/api/startposes/",
            {"run": "http://testserver/api/runs/testrun/", "data": "d", "weight": 1.0},
            format="json",
        )
        assert response.status_code == 201
        response = client.post(
            "/api/startposes/",
            {"run": "http://testserver/api/runs/testrun/", "data": "e", "weight": 0.5},
            format="json",
        )
        assert response.status_code == 201

        recompute_startpos_cumulative_weights()

        self.r1.refresh_from_db()
        self.r1.startpos_locked = False
        self.r1.selfplay_startpos_probability = 0.5
        self.r1.save()

        random.seed(1234567)
        results = {}
        num_ret = [0, 0, 0, 0, 0]
        for i in range(100):
            response = client.post(
                "/api/tasks/",
                {
                    "git_revision": "abcdef123456abcdef123456abcdef1234567890",
                    "task_rep_factor": 4,
                },
                format="multipart",
            )
            assert response.status_code == 200
            for data in response.data["start_poses"]:
                if data not in results:
                    results[data] = 0
                results[data] += 1
            num_ret[len(response.data["start_poses"])] += 1

        assert str(results) == "{'d': 15, 'c': 99, 'a': 54, 'e': 4, 'b': 25}"
        assert str(num_ret) == "[10, 22, 35, 27, 6]"

    def test_bulk_create(self):
        StartPos.objects.filter(run=self.r1).delete()
        client = APIClient()
        client.login(username="test", password="test")

        self.r1.startpos_locked = True
        self.r1.selfplay_startpos_probability = 0.5
        self.r1.save()
        response = client.post(
            "/api/startposes/",
            [
                {
                    "run": "http://testserver/api/runs/testrun/",
                    "data": "a",
                    "weight": 1.125,
                },
                {
                    "run": "http://testserver/api/runs/testrun/",
                    "data": "a",
                    "weight": 5.125,
                },
                {
                    "run": "http://testserver/api/runs/testrun/",
                    "data": "a",
                    "weight": 3.125,
                },
                {
                    "run": "http://testserver/api/runs/testrun/",
                    "data": "a",
                    "weight": 8.25,
                },
            ],
            format="json",
        )
        assert response.status_code == 201
        recompute_startpos_cumulative_weights()
        self.r1.refresh_from_db()
        assert self.r1.startpos_total_weight == 17.625


class TestGetTaskActive:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.5,
            status="Inactive",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
        )

    def teardown_method(self):
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_job_fail(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.status = "Inactive"
        self.r1.save()
        response = client.post(
            "/api/tasks/",
            {
                "git_revision": "abcdef123456abcdef123456abcdef1234567890",
                "allow_rating_task": False,
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        assert str(data) == """{'error': 'No active run.'}"""
        assert response.status_code == 404

    def test_get_job_success(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.status = "Active"
        self.r1.save()
        response = client.post(
            "/api/tasks/",
            {
                "git_revision": "abcdef123456abcdef123456abcdef1234567890",
                "allow_rating_task": False,
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
        )
        assert response.status_code == 200
        assert (
            UserLastVersion.objects.filter(user__username="test").first().git_revision
            == "abcdef123456abcdef123456abcdef1234567890"
        )


class TestGetTaskWhiteList:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.u2 = User.objects.create_user(username="tester", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.5,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
            restrict_to_user_whitelist=False,
            user_whitelist="#test\ntester#test",
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
        )

    def teardown_method(self):
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()
        self.u2.delete()

    def test_get_job_fail_whitelist(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.restrict_to_user_whitelist = True
        self.r1.save()
        response = client.post(
            "/api/tasks/",
            {
                "git_revision": "abcdef123456abcdef123456abcdef1234567890",
                "allow_rating_task": False,
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        assert str(data) == """{'error': 'This run is currently closed except for private testing.'}"""
        assert response.status_code == 403

    def test_get_job_okay_whitelist(self):
        client = APIClient()
        client.login(username="tester", password="test")
        self.r1.restrict_to_user_whitelist = True
        self.r1.save()
        response = client.post(
            "/api/tasks/",
            {
                "git_revision": "abcdef123456abcdef123456abcdef1234567890",
                "allow_rating_task": False,
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
        )
        assert response.status_code == 200

    def test_get_job_okay_without_whitelist(self):
        client = APIClient()
        client.login(username="test", password="test")
        self.r1.restrict_to_user_whitelist = False
        self.r1.save()
        response = client.post(
            "/api/tasks/",
            {
                "git_revision": "abcdef123456abcdef123456abcdef1234567890",
                "allow_rating_task": False,
            },
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
        )
        assert response.status_code == 200


class TestGetSelfplayTaskWithNetworkFile:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork",
            model_file=SimpleUploadedFile(
                "abc.bin.gz",
                base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="),
                content_type="application/gzip",
            ),
            model_file_bytes=28,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            log_gamma_uncertainty=1.5,
            log_gamma_lower_confidence=-3.0,
            log_gamma_upper_confidence=4.0,
            log_gamma_game_count=5,
            is_random=False,
        )

    def teardown_method(self):
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_selfplay_task_with_network(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post(
            "/api/tasks/",
            {"git_revision": "abcdef123456abcdef123456abcdef1234567890"},
            format="multipart",
        )
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': False, 'model_file': 'http://testserver/media/networks/models/testrun/testrun-randomnetwork.bin.gz', 'model_file_bytes': 28, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
        )
        assert response.status_code == 200

    def test_get_selfplay_task_with_network_proxy(self):
        with override_settings(
            NETWORK_USE_PROXY_DOWNLOAD=True,
            NETWORK_PROXY_DOWNLOAD_URL_BASE="https://example.com/",
        ):
            client = APIClient()
            client.login(username="test", password="test")
            response = client.post(
                "/api/tasks/",
                {"git_revision": "abcdef123456abcdef123456abcdef1234567890"},
                format="multipart",
            )
            data = copy.deepcopy(response.data)
            data["network"]["created_at"] = None  # Suppress timestamp for test
            data["run"]["id"] = None  # Suppress id for test
            assert (
                str(data)
                == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': False, 'model_file': 'https://example.com/networks/models/testrun/testrun-randomnetwork.bin.gz', 'model_file_bytes': 28, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'start_poses': []}"""
            )
            assert response.status_code == 200


class TestGetRatingTaskWithNetworkFile:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=1.0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-network0",
            model_file=SimpleUploadedFile(
                "def.bin.gz",
                base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="),
                content_type="application/gzip",
            ),
            model_file_bytes=28,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            log_gamma_uncertainty=1.5,
            log_gamma_lower_confidence=-3.0,
            log_gamma_upper_confidence=4.0,
            log_gamma_game_count=5,
            is_random=False,
        )
        self.n2 = Network.objects.create(
            run=self.r1,
            name="testrun-network1",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
            log_gamma_uncertainty=1.5,
            log_gamma_lower_confidence=-3.0,
            log_gamma_upper_confidence=4.0,
            log_gamma_game_count=5,
            network_size="random",
        )

    def teardown_method(self):
        self.n2.delete()
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_rating_task_with_network(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision": "1111222233334444555566667777888899990000"})
        data = copy.deepcopy(response.data)
        data["white_network"]["created_at"] = None  # Suppress timestamp for test
        data["black_network"]["created_at"] = None  # Suppress timestamp for test
        data["run"]["id"] = None  # Suppress id for test
        assert (
            str(data)
            == """{'kind': 'rating', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'white_network': {'url': 'http://testserver/api/networks/testrun-network1/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network1', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'black_network': {'url': 'http://testserver/api/networks/testrun-network0/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network0', 'created_at': None, 'is_random': False, 'model_file': 'http://testserver/media/networks/models/testrun/testrun-network0.bin.gz', 'model_file_bytes': 28, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}}"""
            or str(data)
            == """{'kind': 'rating', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'white_network': {'url': 'http://testserver/api/networks/testrun-network0/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network0', 'created_at': None, 'is_random': False, 'model_file': 'http://testserver/media/networks/models/testrun/testrun-network0.bin.gz', 'model_file_bytes': 28, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'black_network': {'url': 'http://testserver/api/networks/testrun-network1/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network1', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}}"""
        )
        assert response.status_code == 200
        assert (
            UserLastVersion.objects.filter(user__username="test").first().git_revision
            == "1111222233334444555566667777888899990000"
        )


class TestGetSelfplayTaskWithLargeDelay:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
            min_network_usage_delay=100.0,
            max_network_usage_delay=200.0,
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
        )

    def teardown_method(self):
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_selfplay_task_with_large_delay(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision": "1111222233334444555566667777888899990000"})
        data = response.data
        assert str(data) == """{'error': 'No networks found for run enabled for training games.'}"""
        assert response.status_code == 400


class TestGetRatingTaskWithLargeDelay:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=1.0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
            min_network_usage_delay=100.0,
            max_network_usage_delay=200.0,
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-network0",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            log_gamma_uncertainty=1,
            log_gamma_lower_confidence=-2.0,
            log_gamma_upper_confidence=2.0,
            log_gamma_game_count=3,
            is_random=True,
        )
        self.n2 = Network.objects.create(
            run=self.r1,
            name="testrun-network1",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=1,
            log_gamma_uncertainty=1.5,
            log_gamma_lower_confidence=-3.0,
            log_gamma_upper_confidence=4.0,
            log_gamma_game_count=5,
            is_random=True,
        )

    def teardown_method(self):
        self.n2.delete()
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_rating_task_with_large_delay(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision": "1111222233334444555566667777888899990000"})
        data = response.data
        # A little bit funny of an error message here, but still works
        assert str(data) == """{'error': 'No networks found for run enabled for training games.'}"""
        assert response.status_code == 400


class TestGetNewestNetwork:
    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=1.0,
            status="Active",
            git_revision_hash_whitelist="abcdef123456abcdef123456abcdef1234567890\n\n1111222233334444555566667777888899990000",
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-network0",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            log_gamma_uncertainty=1,
            log_gamma_lower_confidence=-2.0,
            log_gamma_upper_confidence=2.0,
            log_gamma_game_count=3,
            is_random=True,
        )
        self.n2 = Network.objects.create(
            run=self.r1,
            name="testrun-network1",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=1,
            log_gamma_uncertainty=1.5,
            log_gamma_lower_confidence=-3.0,
            log_gamma_upper_confidence=4.0,
            log_gamma_game_count=5,
            is_random=True,
        )

    def teardown_method(self):
        self.n2.delete()
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_get_newest_network(self):
        client = APIClient()
        response = client.get("/api/networks/newest_training/")
        data = copy.deepcopy(response.data)
        data["created_at"] = None  # Suppress timestamp for test
        assert (
            str(data)
            == """{'url': 'http://testserver/api/networks/testrun-network1/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network1', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}"""
        )
        assert response.status_code == 200
