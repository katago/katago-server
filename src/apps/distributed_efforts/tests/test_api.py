import pytest
import copy
import base64

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from src.apps.runs.models import Run
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

    def test_get_job_authenticated_valid_git_revision2(self):
        client = APIClient()
        client.login(username="test", password="test")
        response = client.post("/api/tasks/", {"git_revision":"1111222233334444555566667777888899990000"})
        data = copy.deepcopy(response.data)
        data["white_network"]["created_at"] = None # Suppress timestamp for test
        data["black_network"]["created_at"] = None # Suppress timestamp for test
        data["run"]["id"] = None # Suppress id for test
        assert (str(data) == """{'kind': 'rating', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'white_network': {'url': 'http://testserver/api/networks/testrun-network0/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network0', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'black_network': {'url': 'http://testserver/api/networks/testrun-network1/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network1', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}}""" or
                str(data) == """{'kind': 'rating', 'run': {'id': None, 'url': 'http://testserver/api/runs/testrun/', 'name': 'testrun', 'data_board_len': 19, 'inputs_version': 7, 'max_search_threads_allowed': 8}, 'config': 'FILL ME', 'white_network': {'url': 'http://testserver/api/networks/testrun-network1/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network1', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}, 'black_network': {'url': 'http://testserver/api/networks/testrun-network0/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'testrun-network0', 'created_at': None, 'is_random': True, 'model_file': None, 'model_file_bytes': 0, 'model_file_sha256': '12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd'}}"""
        )
        assert response.status_code == 200



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
        response = client.post("/api/tasks/", {"git_revision":"abcdef123456abcdef123456abcdef1234567890"})
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
        response = client.post("/api/tasks/", {"git_revision":"abcdef123456abcdef123456abcdef1234567890"})
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
        response = client.post("/api/networks/", {
            "run": "http://testserver/api/runs/testrun/",
            "name": "networkname",
            "network_size": "b4c32",
            "is_random": "false",
            "model_file": SimpleUploadedFile("networkname.bin.gz", b"", content_type="application/octet-stream"),
            "model_file_bytes": "0",
            "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }, format='multipart'
        )
        data = copy.deepcopy(response.data)
        assert str(data) == """{'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')}"""
        assert response.status_code == 403

    def test_post_network_empty(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post("/api/networks/", {
            "run": "http://testserver/api/runs/testrun/",
            "name": "networkname2",
            "network_size": "b4c32",
            "is_random": "false",
            "model_file": SimpleUploadedFile("networkname2.bin.gz", b"", content_type="application/octet-stream"),
            "model_file_bytes": "0",
            "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }, format='multipart'
        )
        data = copy.deepcopy(response.data)
        assert str(data) == """{'model_file': [ErrorDetail(string='The submitted file is empty.', code='empty')]}"""
        assert response.status_code == 400

    def test_post_network_not_a_zip(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post("/api/networks/", {
            "run": "http://testserver/api/runs/testrun/",
            "name": "networkname3",
            "network_size": "b4c32",
            "is_random": "false",
            "model_file": SimpleUploadedFile("networkname3.bin.gz", b"Hello world", content_type="text/plain"),
            "model_file_bytes": "1",
            "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }, format='multipart'
        )
        data = copy.deepcopy(response.data)
        assert str(data) == """{'model_file': [ErrorDetail(string='Files of type text/plain are not supported.', code='content_type')]}"""
        assert response.status_code == 400

    def test_post_network_gzip(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post("/api/networks/", {
            "run": "http://testserver/api/runs/testrun/",
            "name": "networkname4",
            "network_size": "b4c32",
            "is_random": "false",
            # "model_file": SimpleUploadedFile("networkname4.bin.gz", b"\x8b\x1f\x08\x08\x61\x0b\x5f\x58\x03\x00\x62\x61\x2e\x63\x78\x74\x00\x74\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00", content_type="application/gzip"),
            "model_file": SimpleUploadedFile("networkname4.bin.gz", base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="), content_type="application/gzip"),
            "model_file_bytes": "28",
            "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
        }, format='multipart'
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None # Suppress timestamp for test
        data["model_file"] = data["model_file"][0:56] + "..."
        assert str(data) == """{'url': 'http://testserver/api/networks/networkname4/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname4', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/testrun/networkname4.bi...', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': None, 'notes': '', 'log_gamma': 0.0, 'log_gamma_uncertainty': 0.0, 'log_gamma_lower_confidence': 0.0, 'log_gamma_upper_confidence': 0.0}"""
        assert response.status_code == 201

    def test_post_network_loggamma_only(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post("/api/networks/", {
            "run": "http://testserver/api/runs/testrun/",
            "name": "networkname4b",
            "network_size": "b4c32",
            "is_random": "false",
            "model_file": SimpleUploadedFile("networkname4b.bin.gz", base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="), content_type="application/gzip"),
            "model_file_bytes": "28",
            "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
            "log_gamma": "4",
        }, format='multipart'
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None # Suppress timestamp for test
        data["model_file"] = data["model_file"][0:56] + "..."
        assert str(data) == """{'url': 'http://testserver/api/networks/networkname4b/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname4b', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/testrun/networkname4b.b...', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': None, 'notes': '', 'log_gamma': 4.0, 'log_gamma_uncertainty': 2.0, 'log_gamma_lower_confidence': 0.0, 'log_gamma_upper_confidence': 8.0}"""
        assert response.status_code == 201

    def test_post_network_loggamma_partial(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post("/api/networks/", {
            "run": "http://testserver/api/runs/testrun/",
            "name": "networkname5",
            "network_size": "b4c32",
            "is_random": "false",
            "model_file": SimpleUploadedFile("networkname5.bin.gz", base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="), content_type="application/gzip"),
            "model_file_bytes": "28",
            "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
            "log_gamma": "4",
            "log_gamma_uncertainty": "1.5",
        }, format='multipart'
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None # Suppress timestamp for test
        data["model_file"] = data["model_file"][0:56] + "..."
        assert str(data) == """{'url': 'http://testserver/api/networks/networkname5/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname5', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/testrun/networkname5.bi...', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': None, 'notes': '', 'log_gamma': 4.0, 'log_gamma_uncertainty': 1.5, 'log_gamma_lower_confidence': 1.0, 'log_gamma_upper_confidence': 7.0}"""
        assert response.status_code == 201

    def test_post_network_loggamma_full(self):
        client = APIClient()
        client.login(username="testadmin", password="testadmin")
        response = client.post("/api/networks/", {
            "run": "http://testserver/api/runs/testrun/",
            "name": "networkname6",
            "network_size": "b4c32",
            "is_random": "false",
            "model_file": SimpleUploadedFile("networkname6.bin.gz", base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="), content_type="application/gzip"),
            "model_file_bytes": "28",
            "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
            "log_gamma": "4",
            "log_gamma_uncertainty": "2",
            "log_gamma_lower_confidence": "3",
            "log_gamma_upper_confidence": "7",
        }, format='multipart'
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None # Suppress timestamp for test
        data["model_file"] = data["model_file"][0:56] + "..."
        assert str(data) == """{'url': 'http://testserver/api/networks/networkname6/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname6', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/testrun/networkname6.bi...', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': None, 'notes': '', 'log_gamma': 4.0, 'log_gamma_uncertainty': 2.0, 'log_gamma_lower_confidence': 3.0, 'log_gamma_upper_confidence': 7.0}"""
        assert response.status_code == 201

        response = client.post("/api/networks/", {
            "run": "http://testserver/api/runs/testrun/",
            "name": "networkname7",
            "network_size": "b4c32",
            "is_random": "false",
            "model_file": SimpleUploadedFile("networkname7.bin.gz", base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="), content_type="application/gzip"),
            "model_file_bytes": "28",
            "model_file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 hash is actually NOT right, but it's not checked
            "parent_network": "http://testserver/api/networks/networkname6/"
        }, format='multipart'
        )
        data = copy.deepcopy(response.data)
        data["created_at"] = None # Suppress timestamp for test
        data["model_file"] = data["model_file"][0:56] + "..."
        assert str(data) == """{'url': 'http://testserver/api/networks/networkname7/', 'run': 'http://testserver/api/runs/testrun/', 'name': 'networkname7', 'created_at': None, 'network_size': 'b4c32', 'is_random': False, 'training_games_enabled': False, 'rating_games_enabled': False, 'model_file': 'http://testserver/media/networks/testrun/networkname7.bi...', 'model_file_bytes': 28, 'model_file_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'model_zip_file': None, 'parent_network': 'http://testserver/api/networks/networkname6/', 'notes': '', 'log_gamma': 4.0, 'log_gamma_uncertainty': 2.0, 'log_gamma_lower_confidence': 0.0, 'log_gamma_upper_confidence': 8.0}"""
        assert response.status_code == 201

