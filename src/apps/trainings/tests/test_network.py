import pytest
import math
import base64
import copy

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from src.apps.runs.models import Run
from src.apps.trainings.models import Network
from src.apps.games.models import RatingGame, TrainingGame, GameCountByNetwork, GameCountByUser

pytestmark = pytest.mark.django_db

User = get_user_model()

fake_sha256 = "12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd"

class TestNetworkValidation:

    def setup_method(self):
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.0,
            status="Active",
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="testrun-a",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
            network_size="random",
            train_step=0,
            total_num_data_rows=0,
        )
        self.n2 = Network.objects.create(
            run=self.r1,
            name="testrun-b",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=False,
            network_size="b4c32",
            train_step=0,
            total_num_data_rows=0,
        )
        self.n3 = Network.objects.create(
            run=self.r1,
            name="testrun-c",
            model_file=SimpleUploadedFile("networkname2.bin.gz", b"", content_type="application/octet-stream"),
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=False,
            network_size="b4c32",
            train_step=0,
            total_num_data_rows=0,
        )
        self.n4 = Network.objects.create(
            run=self.r1,
            name="testrun-d",
            model_file=SimpleUploadedFile("networkname4.bin.gz", base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="), content_type="application/gzip"),
            model_file_bytes=0, # file length is not actually checked
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=False,
            network_size="b4c32",
            train_step=0,
            total_num_data_rows=0,
        )
        self.n5 = Network.objects.create(
            run=self.r1,
            name="testrun-e",
            model_file=SimpleUploadedFile("networkname5.bin.gz", base64.decodebytes(b"H4sICAthWF8AA2FiYy50eHQAAwAAAAAAAAAAAA=="), content_type="application/gzip"),
            model_file_bytes=28,
            model_file_sha256=fake_sha256, # sha256 is actually not checked
            log_gamma=0,
            is_random=False,
            network_size="b4c32",
            train_step=0,
            total_num_data_rows=0,
        )
        self.n6 = Network.objects.create(
            run=self.r1,
            name="testrun!",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
            network_size="random",
            train_step=0,
            total_num_data_rows=0,
        )

    def teardown_method(self):
        self.n1.delete()
        self.n2.delete()
        self.n3.delete()
        self.n4.delete()
        self.n5.delete()
        self.n6.delete()
        self.r1.delete()

    def test_network_validations(self):
        self.n1.full_clean()
        with pytest.raises(ValidationError):
            self.n2.full_clean()
        with pytest.raises(ValidationError):
            self.n3.full_clean()
        self.n4.full_clean()
        self.n5.full_clean()
        with pytest.raises(ValidationError):
            self.n6.full_clean()
