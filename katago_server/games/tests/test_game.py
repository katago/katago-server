import pytest
import math

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from katago_server.runs.models import Run
from katago_server.games.models import RatingGame
from katago_server.trainings.models import Network
from katago_server.games.models import TrainingGame

pytestmark = pytest.mark.django_db

User = get_user_model()

fake_sha256 = "12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd"

def create_training_game(
        run,
        submitted_by,
        winner=RatingGame.GamesResult.BLACK,
        board_size_x=19,
        board_size_y=19,
        handicap=0,
        komi=7.0,
        rules={},
        extra_metadata={},
        score=100.0,
        resigned=False,
        black_network=None,
        white_network=None,
        sgf_file=SimpleUploadedFile(name='game.sgf', content=b"(;GM[1]FF[4]CA[UTF-8]ST[2]RU[Japanese]SZ[19]KM[0])", content_type='text/plain'),
        training_data_file=SimpleUploadedFile(name='game.npz', content=b"\x50\x4b\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", content_type='application/octet-stream'),
        kg_game_uid="12341234ABCDABCD",
):
    return TrainingGame.objects.create(
        run=run,
        submitted_by=submitted_by,
        winner=winner,
        board_size_x=board_size_x,
        board_size_y=board_size_y,
        handicap=handicap,
        komi=komi,
        rules=rules,
        extra_metadata=extra_metadata,
        score=score,
        resigned=resigned,
        black_network=black_network,
        white_network=white_network,
        sgf_file=sgf_file,
        training_data_file=training_data_file,
        kg_game_uid=kg_game_uid,
    )
def create_rating_game(
        run,
        submitted_by,
        winner=RatingGame.GamesResult.BLACK,
        board_size_x=19,
        board_size_y=19,
        handicap=0,
        komi=7.0,
        rules={},
        extra_metadata={},
        score=100.0,
        resigned=False,
        black_network=None,
        white_network=None,
        sgf_file=SimpleUploadedFile(name='game.sgf', content=b"(;GM[1]FF[4]CA[UTF-8]ST[2]RU[Japanese]SZ[19]KM[0])", content_type='text/plain'),
        kg_game_uid="12341234ABCDABCD",
):
    return RatingGame.objects.create(
        run=run,
        submitted_by=submitted_by,
        winner=winner,
        board_size_x=board_size_x,
        board_size_y=board_size_y,
        handicap=handicap,
        komi=komi,
        rules=rules,
        extra_metadata=extra_metadata,
        score=score,
        resigned=resigned,
        black_network=black_network,
        white_network=white_network,
        sgf_file=sgf_file,
        kg_game_uid=kg_game_uid,
    )


class TestGame:

    def setup_method(self):
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.0,
            status="Active",
            elo_number_of_iterations = 50,
            virtual_draw_strength = 4.0,
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
        self.u1 = User.objects.create_user(username="test", password="test")
        self.good_games = []
        self.bad_games = []
        self.good_games.extend(self.create_games_with_defaults(komi=-115.5))
        self.bad_games.extend(self.create_games_with_defaults(komi=13.6))
        self.good_games.extend(self.create_games_with_defaults(score=500))
        self.good_games.extend(self.create_games_with_defaults(score=0.5))
        self.bad_games.extend(self.create_games_with_defaults(score=0.1))
        self.good_games.extend(self.create_games_with_defaults(board_size_x=13))
        self.bad_games.extend(self.create_games_with_defaults(board_size_x=2))
        self.bad_games.extend(self.create_games_with_defaults(board_size_x=45))
        self.bad_games.extend(self.create_games_with_defaults(board_size_y=2))
        self.bad_games.extend(self.create_games_with_defaults(board_size_y=45))
        self.bad_games.extend(self.create_games_with_defaults(handicap=25))
        self.bad_games.extend(self.create_games_with_defaults(handicap=-1))
        self.good_games.extend(self.create_games_with_defaults(handicap=1))
        self.good_games.extend(self.create_games_with_defaults(handicap=7))
        self.bad_games.extend(self.create_games_with_defaults(
            sgf_file=SimpleUploadedFile(name='game.sgf', content=b"NOT AN SGF", content_type='text/plain')
        ))
        self.bad_games.extend(self.create_games_with_defaults(
            training_data_file=SimpleUploadedFile(name='game.npz', content=b"NOT A ZIP", content_type='application/octet-stream')
        ))


    def create_games_with_defaults(self, **kwargs):
        traininggame = create_training_game(
            run=self.r1,
            submitted_by=self.u1,
            black_network=self.n1,
            white_network=self.n1,
            **kwargs
        )
        if "training_data_file" in kwargs:
            return [traininggame]
        ratinggame = create_rating_game(
            run=self.r1,
            submitted_by=self.u1,
            black_network=self.n1,
            white_network=self.n1,
            **kwargs
        )
        return [traininggame,ratinggame]

    def teardown_method(self):
        for game in self.good_games:
            game.delete()
        for game in self.bad_games:
            game.delete()
        self.u1.delete()
        self.n1.delete()
        self.r1.delete()

    def test_elos(self):
        for game in self.good_games:
            game.full_clean()
        for game in self.bad_games:
            with pytest.raises(ValidationError):
                game.full_clean()
        pass
