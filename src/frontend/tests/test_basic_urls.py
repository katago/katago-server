import base64

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from src.apps.games.models import GameCountByNetwork, GameCountByUser, RatingGame, TrainingGame
from src.apps.games.tests.test_game import goodnpzbase64
from src.apps.runs.models import Run
from src.apps.trainings.models import Network

pytestmark = pytest.mark.django_db

User = get_user_model()

fake_sha256 = "12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd"


class TestUrlsEmptySite:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_urls(self):
        client = Client()
        assert client.get("/").status_code == 200
        assert client.get("/healthz/").status_code == 200
        assert client.get("/runs/").status_code == 200
        assert client.get("/runs//").status_code == 404
        assert client.get("/runs/123/").status_code == 404
        assert client.get("/runs/run0/").status_code == 404
        assert client.get("/networks/").status_code == 200
        assert client.get("/networks/run0/").status_code == 404
        assert client.get("/networks/run0/run0-foo/").status_code == 404
        assert client.get("/networks/run0/run0-foo/rating-games/").status_code == 404
        assert client.get("/networks/run0/run0-foo/training-games/").status_code == 404
        assert client.get("/networks/").status_code == 200
        assert client.get("/games/").status_code == 200
        assert client.get("/games/run0/").status_code == 404
        assert client.get("/contributions/").status_code == 200
        assert client.get("/contributions/run0/").status_code == 404
        assert client.get("/contributions/run1/").status_code == 404
        assert client.get("/contributions/abc/").status_code == 404
        assert client.get("/contributions/abc/training-games/").status_code == 404
        assert client.get("/contributions/abc/rating-games/").status_code == 404
        assert client.get("/sgfplayer/").status_code == 404
        assert client.get("/sgfplayer/training-games/").status_code == 404
        assert client.get("/sgfplayer/rating-games/").status_code == 404
        assert client.get("/sgfplayer/training-games/10/").status_code == 404
        assert client.get("/sgfplayer/rating-games/10/").status_code == 404
        assert client.get("/sgfplayer/training-games/abc/").status_code == 404
        assert client.get("/sgfplayer/rating-games/abc/").status_code == 404


class TestUrlsSimpleSite:
    def setup_method(self):
        self.u0 = User.objects.create_user(username="abc", password="test")
        self.r0 = Run.objects.create(
            name="run0",
            rating_game_probability=0.0,
            status="Inactive",
            elo_number_of_iterations=50,
            virtual_draw_strength=4.0,
        )
        self.r1 = Run.objects.create(
            name="run1",
            rating_game_probability=0.0,
            status="Active",
            elo_number_of_iterations=50,
            virtual_draw_strength=4.0,
        )
        self.n0 = Network.objects.create(
            run=self.r1,
            name="run1-foo",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
        )
        self.n1 = Network.objects.create(
            run=self.r1,
            name="run1-bar",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
            parent_network=self.n0,
        )
        self.g0 = TrainingGame.objects.create(
            run=self.r1,
            submitted_by=self.u0,
            winner=RatingGame.GamesResult.BLACK,
            board_size_x=19,
            board_size_y=19,
            handicap=3,
            komi=0.5,
            gametype="normal",
            rules="",
            extra_metadata={},
            score=6.5,
            resigned=False,
            game_length=120,
            black_network=self.n1,
            white_network=self.n1,
            sgf_file=SimpleUploadedFile(
                name="game.sgf",
                content=b"(;GM[1]FF[4]CA[UTF-8]ST[2]RU[Japanese]SZ[19]KM[0])",
                content_type="text/plain",
            ),
            training_data_file=SimpleUploadedFile(
                name="game.npz", content=base64.decodebytes(goodnpzbase64), content_type="application/octet-stream"
            ),
            num_training_rows=5,
            kg_game_uid="1234abcd",
        )
        self.g1 = RatingGame.objects.create(
            run=self.r1,
            submitted_by=self.u0,
            winner=RatingGame.GamesResult.WHITE,
            board_size_x=15,
            board_size_y=16,
            handicap=0,
            komi=6.5,
            gametype="normal",
            rules="",
            extra_metadata={},
            score=-1.5,
            resigned=False,
            game_length=120,
            black_network=self.n1,
            white_network=self.n0,
            sgf_file=SimpleUploadedFile(
                name="game.sgf",
                content=b"(;GM[1]FF[4]CA[UTF-8]ST[2]RU[Japanese]SZ[19]KM[0])",
                content_type="text/plain",
            ),
            kg_game_uid="2345abcd",
        )

    def teardown_method(self):
        self.g1.delete()
        self.g0.delete()
        self.n1.delete()
        self.n0.delete()
        self.r1.delete()
        self.r0.delete()
        self.u0.delete()
        pass

    def test_urls(self):
        client = Client()
        assert client.get("/").status_code == 200
        assert client.get("/healthz/").status_code == 200
        assert client.get("/runs/").status_code == 200
        assert client.get("/runs//").status_code == 404
        assert client.get("/runs/123/").status_code == 404
        assert client.get("/runs/run0/").status_code == 200
        assert client.get("/runs/run1/").status_code == 200
        assert client.get("/runs/run2/").status_code == 404
        assert client.get("/networks/").status_code == 200
        assert client.get("/networks/run0/").status_code == 200
        assert client.get("/networks/run1/").status_code == 200
        assert client.get("/networks/run2/").status_code == 404
        assert client.get("/networks/run0/run0-foo/").status_code == 404
        assert client.get("/networks/run0/run1-foo/").status_code == 404
        assert client.get("/networks/run1/run1-foo/").status_code == 404
        assert client.get("/networks/run1/run1-bar/").status_code == 404
        assert client.get("/networks/run1/run1-fooo/").status_code == 404
        assert client.get("/networks/run0/run0-foo/rating-games/").status_code == 404
        assert client.get("/networks/run0/run1-foo/rating-games/").status_code == 404
        assert client.get("/networks/run1/run1-foo/rating-games/").status_code == 200
        assert client.get("/networks/run1/run1-bar/rating-games/").status_code == 200
        assert client.get("/networks/run1/run1-fooo/rating-games/").status_code == 404
        assert client.get("/networks/run0/run0-foo/training-games/").status_code == 404
        assert client.get("/networks/run0/run1-foo/training-games/").status_code == 404
        assert client.get("/networks/run1/run1-foo/training-games/").status_code == 200
        assert client.get("/networks/run1/run1-bar/training-games/").status_code == 200
        assert client.get("/networks/run1/run1-fooo/training-games/").status_code == 404
        assert client.get("/networks/").status_code == 200
        assert client.get("/games/").status_code == 200
        assert client.get("/games//").status_code == 404
        assert client.get("/games/run0/").status_code == 200
        assert client.get("/games/run1/").status_code == 200
        assert client.get("/contributions/").status_code == 200
        assert client.get("/contributions/run0/").status_code == 200
        assert client.get("/contributions/run1/").status_code == 200
        assert client.get("/contributions/abc/").status_code == 404
        assert client.get("/contributions/run0/training-games/").status_code == 404
        assert client.get("/contributions/run1/training-games/").status_code == 404
        assert client.get("/contributions/abc/training-games/").status_code == 200
        assert client.get("/contributions/abc/rating-games/").status_code == 200
        assert client.get("/sgfplayer/").status_code == 404
        assert client.get("/sgfplayer/training-games/").status_code == 404
        assert client.get("/sgfplayer/rating-games/").status_code == 404
        assert client.get("/sgfplayer/training-games/%d/" % self.g0.id).status_code == 200
        assert client.get("/sgfplayer/rating-games/%d/" % self.g0.id).status_code == 404
        assert client.get("/sgfplayer/training-games/%d/" % self.g1.id).status_code == 404
        assert client.get("/sgfplayer/rating-games/%d/" % self.g1.id).status_code == 200
        assert client.get("/sgfplayer/training-games/abc/").status_code == 404
