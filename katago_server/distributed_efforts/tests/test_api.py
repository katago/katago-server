import pytest
import copy

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from katago_server.runs.models import Run
from katago_server.trainings.models import Network

pytestmark = pytest.mark.django_db

User = get_user_model()

fake_sha256 = "12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd"

class TestGetTaskSimple:

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
        assert str(response.data) == """{'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')}"""
        response = client.post("/api/tasks/", {"git_revision":"abcdef123456abcdef123456abcdef1234567890"})
        assert response.status_code == 401
        assert str(response.data) == """{'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')}"""

    def test_get_job_authenticated_no_git_revision(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {})
        assert response.status_code == 400
        assert str(response.data) == """{'error': "This version of KataGo is not usable for distributed because either it's had custom modifications or has been compiled without version info."}"""

    def test_get_job_authenticated_blank_git_revision(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision":""})
        assert response.status_code == 400
        assert str(response.data) == """{'error': "This version of KataGo is not usable for distributed because either it's had custom modifications or has been compiled without version info."}"""

    def test_get_job_authenticated_short_git_revision(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision":"abcd"})
        assert response.status_code == 400
        assert str(response.data) == """{'error': "This version of KataGo is not usable for distributed because either it's had custom modifications or has been compiled without version info."}"""

    def test_get_job_authenticated_bad_git_revision(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision":"0000111122223333444455556666777788889999"})
        assert response.status_code == 400
        assert str(response.data) == """{'error': 'This version of KataGo is not enabled for distributed. If this is an official version and/or you think this is an oversight, please ask server admins to enable the following version hash: 0000111122223333444455556666777788889999'}"""

    def test_get_job_authenticated_valid_git_revision1(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision":"abcdef123456abcdef123456abcdef1234567890"})
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None # Suppress timestamp for test
        data["run"]["id"] = None # Suppress id for test
        assert str(data) == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}}"""
        assert response.status_code == 200

    def test_get_job_authenticated_valid_git_revision1_multipart(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision":"abcdef123456abcdef123456abcdef1234567890"},format="multipart")
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None # Suppress timestamp for test
        data["run"]["id"] = None # Suppress id for test
        assert str(data) == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}}"""
        assert response.status_code == 200

    def test_get_job_authenticated_valid_git_revision2(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision":"1111222233334444555566667777888899990000"})
        data = copy.deepcopy(response.data)
        data["network"]["created_at"] = None # Suppress timestamp for test
        data["run"]["id"] = None # Suppress id for test
        assert str(data) == """{'kind': 'selfplay', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'network': {'url': 'http://testserver/api/networks/testrun-randomnetwork/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-randomnetwork', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}}"""
        assert response.status_code == 200
