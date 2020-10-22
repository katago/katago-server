import pytest
import math
import base64

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

goodnpzbase64 = b"UEsDBBQAAgAIACgvJ1G3q7wfbQAAAPQEAAAVAAAAYmluYXJ5SW5wdXROQ0hXUGFja2Vkm+wX6hsQycjwjaFaPSW1OLlI3Uq9ptRQXUc9Lb+opCgxLz6/KCUVKOqWmFOcqqNenJFYkKpupWGoY2SkY2KmWaswpAHXBwY5BuYDDBUMRAI2BtIAUwPDIAGDxyW0AyykhgmN1ILBCAjvoZkbAFBLAwQUAAIACAAoLydRPC6Dg1oAAABMAQAADQAAAGdsb2JhbElucHV0TkOb7BfqGxDJyPCNoVo9JbU4uUjdSt0mzURdRz0tv6ikKDEvPr8oJRUo6paYU5yqo16ckViQqm6lYahjaKlZqzDUARcDQ4M9Axq4NXOlHVR8PwNOgKrvw6/9dgBQSwMEFAACAAgAKC8nUfcZaStZAAAAqAYAABMAAABwb2xpY3lUYXJnZXRzTkNNb3Zlm+wX6hsQycjwjaFaPSW1OLlI3UrdJtNIXUc9Lb+opCgxLz6/KCUVKOqWmFOcqqNenJFYkKpupWGoY6RjbGakWaswpAEXA5GAiWEUjIKhAEwYGEfhKBxmEABQSwMEFAACAAgAKC8nURKSnqvDAAAAAAIAAA8AAABnbG9iYWxUYXJnZXRzTkOb7BfqGxDJyPCNoVo9JbU4uUjdSt0mzURdRz0tv6ikKDEvPr8oJRUo6paYU5yqo16ckViQqm6lYahjZqJZqzDUARcDQ4M9AxQEMlxxWFlSZf8ia6MNiO/Bccoh6nqJfVyXkS2I//H9foe96vn2cofawPy127Y6nLmeZb/YcSWYv//rWgeQGQwMDvY55+/bMMAByA4YhvGRAbocKq5htvNSqEjyTOiY5TFD67SnjGGa14LYbx4Qu5DNWuDAQBAscELmAQBQSwMEFAACAAgAKC8nUYN/ouZQAAAASgQAAAsAAABzY29yZURpc3RyTpvsF+obEMnI8I2hWj0ltTi5SN1KvSbTUF1HPS2/qKQoMS8+vyglFSjqlphTnKqjXpyRWJCqbqVhqGNhYqRZqzDEARfDKBgqIJx3NAwGMQAAUEsDBBQAAgAIACgvJ1HEPGydZwAAAA0IAAAQAAAAdmFsdWVUYXJnZXRzTkNIV5vsF+obEMnI8I2hWj0ltTi5SN1KvSbTUF1HPS2/qKQoMS8+vyglFSjqlphTnKqjXpyRWJCqbqVhqGOqY2gJRJq1CkMYcDFgA4yMaAL/gXAUjIIhC0ZT9GhADy9QUYEm0AGEo4AiAABQSwECPwMUAAIACAAoLydRt6u8H20AAAD0BAAAFQAAAAAAAAAAAAAAtoEAAAAAYmluYXJ5SW5wdXROQ0hXUGFja2VkUEsBAj8DFAACAAgAKC8nUTwug4NaAAAATAEAAA0AAAAAAAAAAAAAALaBoAAAAGdsb2JhbElucHV0TkNQSwECPwMUAAIACAAoLydR9xlpK1kAAACoBgAAEwAAAAAAAAAAAAAAtoElAQAAcG9saWN5VGFyZ2V0c05DTW92ZVBLAQI/AxQAAgAIACgvJ1ESkp6rwwAAAAACAAAPAAAAAAAAAAAAAAC2ga8BAABnbG9iYWxUYXJnZXRzTkNQSwECPwMUAAIACAAoLydRg3+i5lAAAABKBAAACwAAAAAAAAAAAAAAtoGfAgAAc2NvcmVEaXN0ck5QSwECPwMUAAIACAAoLydRxDxsnWcAAAANCAAAEAAAAAAAAAAAAAAAtoEYAwAAdmFsdWVUYXJnZXRzTkNIV1BLBQYAAAAABgAGAHMBAACtAwAAAAA="

def create_training_game(
        run,
        submitted_by,
        winner=RatingGame.GamesResult.BLACK,
        board_size_x=19,
        board_size_y=19,
        handicap=0,
        komi=7.0,
        gametype="normal",
        rules={},
        extra_metadata={},
        score=100.0,
        resigned=False,
        game_length=0,
        black_network=None,
        white_network=None,
        sgf_file=SimpleUploadedFile(name='game.sgf', content=b"(;GM[1]FF[4]CA[UTF-8]ST[2]RU[Japanese]SZ[19]KM[0])", content_type='text/plain'),
        training_data_file=SimpleUploadedFile(name='game.npz', content=base64.decodebytes(goodnpzbase64), content_type='application/octet-stream'),
        num_training_rows = 0,
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
        gametype=gametype,
        rules=rules,
        extra_metadata=extra_metadata,
        score=score,
        resigned=resigned,
        game_length=game_length,
        black_network=black_network,
        white_network=white_network,
        sgf_file=sgf_file,
        training_data_file=training_data_file,
        num_training_rows=num_training_rows,
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
        gametype="normal",
        rules={},
        extra_metadata={},
        score=100.0,
        resigned=False,
        game_length=0,
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
        gametype=gametype,
        rules=rules,
        extra_metadata=extra_metadata,
        score=score,
        resigned=resigned,
        game_length=game_length,
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
        self.bad_games.extend(self.create_games_with_defaults(handicap=2500))
        self.bad_games.extend(self.create_games_with_defaults(handicap=-1))
        self.good_games.extend(self.create_games_with_defaults(handicap=1))
        self.good_games.extend(self.create_games_with_defaults(handicap=7))
        self.bad_games.extend(self.create_games_with_defaults(
            sgf_file=SimpleUploadedFile(name='game.sgf', content=b"NOT AN SGF", content_type='text/plain')
        ))
        self.bad_games.extend(self.create_games_with_defaults(
            training_data_file=SimpleUploadedFile(name='game.npz', content=b"NOT A ZIP", content_type='application/octet-stream')
        ))
        self.bad_games.extend(self.create_games_with_defaults(
            training_data_file=SimpleUploadedFile(name='game.npz', content=b"\x50\x4b\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", content_type='application/octet-stream')
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

    def test_game_validations(self):
        for game in self.good_games:
            game.full_clean()
        for game in self.bad_games:
            with pytest.raises(ValidationError):
                game.full_clean()
        pass


class TestMaterializedGameViews:

    def setup_method(self):
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.0,
            status="Active",
        )
        self.r2 = Run.objects.create(
            name="testrun2",
            rating_game_probability=0.0,
            status="Active",
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
        )
        self.n3 = Network.objects.create(
            run=self.r2,
            name="testrun-randomnetwork3",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
        )
        self.n4 = Network.objects.create(
            run=self.r2,
            name="testrun-randomnetwork4",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
        )
        self.u1 = User.objects.create_user(username="testuser", password="test")
        self.u2 = User.objects.create_user(username="testuser2", password="test")

        self.games = []

        self.games.append(self.create_game_with_defaults(
            kind = "training",
            run=self.r1,
            submitted_by=self.u1,
            black_network=self.n1,
            white_network=self.n1,
        ))
        self.games.append(self.create_game_with_defaults(
            kind = "training",
            run=self.r1,
            submitted_by=self.u1,
            black_network=self.n1,
            white_network=self.n1,
        ))
        self.games.append(self.create_game_with_defaults(
            kind = "training",
            run=self.r1,
            submitted_by=self.u1,
            black_network=self.n2,
            white_network=self.n2,
        ))
        self.games.append(self.create_game_with_defaults(
            kind = "rating",
            run=self.r1,
            submitted_by=self.u2,
            black_network=self.n1,
            white_network=self.n2,
            winner=RatingGame.GamesResult.BLACK,
        ))
        self.games.append(self.create_game_with_defaults(
            kind = "rating",
            run=self.r1,
            submitted_by=self.u2,
            black_network=self.n1,
            white_network=self.n2,
            winner=RatingGame.GamesResult.DRAW,
        ))
        self.games.append(self.create_game_with_defaults(
            kind = "rating",
            run=self.r2,
            submitted_by=self.u1,
            black_network=self.n3,
            white_network=self.n4,
            winner=RatingGame.GamesResult.WHITE,
        ))
        self.games.append(self.create_game_with_defaults(
            kind = "rating",
            run=self.r2,
            submitted_by=self.u1,
            black_network=self.n3,
            white_network=self.n4,
            winner=RatingGame.GamesResult.WHITE,
        ))
        self.games.append(self.create_game_with_defaults(
            kind = "rating",
            run=self.r2,
            submitted_by=self.u2,
            black_network=self.n4,
            white_network=self.n3,
            winner=RatingGame.GamesResult.WHITE,
        ))
        self.games.append(self.create_game_with_defaults(
            kind = "training",
            run=self.r2,
            submitted_by=self.u2,
            black_network=self.n4,
            white_network=self.n4,
        ))
        self.games.append(self.create_game_with_defaults(
            kind = "training",
            run=self.r2,
            submitted_by=self.u2,
            black_network=self.n4,
            white_network=self.n4,
        ))
        self.games.append(self.create_game_with_defaults(
            kind = "training",
            run=self.r2,
            submitted_by=self.u1,
            black_network=self.n4,
            white_network=self.n4,
        ))


    def create_game_with_defaults(self, kind, **kwargs):
        if kind == "training":
            traininggame = create_training_game(
                **kwargs
            )
            return traininggame
        else:
            ratinggame = create_rating_game(
                **kwargs
            )
            return ratinggame

    def teardown_method(self):
        for game in self.games:
            game.delete()
        self.u1.delete()
        self.u2.delete()
        self.n1.delete()
        self.n2.delete()
        self.n3.delete()
        self.n4.delete()
        self.r1.delete()
        self.r2.delete()

    def test_views(self):
        def game_count_by_network_str(obj):
            return {
                "network": obj.network.name,
                "run": obj.run.name,
                "network_name": obj.network_name,
                "total_num_training_games": obj.total_num_training_games,
                "total_num_training_rows": obj.total_num_training_rows,
                "total_num_rating_games": obj.total_num_rating_games,
                "total_rating_score": obj.total_rating_score,
            }

        def game_count_by_user_str(obj):
            return {
                "user": obj.user.username,
                "run": obj.run.name,
                "username": obj.username,
                "total_num_training_games": obj.total_num_training_games,
                "total_num_training_rows": obj.total_num_training_rows,
                "total_num_rating_games": obj.total_num_rating_games,
            }
        for game in self.games:
            game.full_clean()
        s = "\n"
        for obj in GameCountByNetwork.objects.all().order_by("network_name"):
            s += str(game_count_by_network_str(obj)) + "\n"
        assert(s == "\n")
        s = "\n"
        for obj in GameCountByUser.objects.all().order_by("username","run__name"):
            s += str(game_count_by_user_str(obj)) + "\n"
        assert(s == "\n")
        GameCountByNetwork.refresh()
        GameCountByUser.refresh()
        s = "\n"
        for obj in GameCountByNetwork.objects.all().order_by("network_name"):
            s += str(game_count_by_network_str(obj)) + "\n"
        assert(s == """
{'network': 'testrun-randomnetwork', 'run': 'testrun', 'network_name': 'testrun-randomnetwork', 'total_num_training_games': 2, 'total_num_training_rows': 0, 'total_num_rating_games': Decimal('2'), 'total_rating_score': Decimal('1.5')}
{'network': 'testrun-randomnetwork2', 'run': 'testrun', 'network_name': 'testrun-randomnetwork2', 'total_num_training_games': 1, 'total_num_training_rows': 0, 'total_num_rating_games': Decimal('2'), 'total_rating_score': Decimal('0.5')}
{'network': 'testrun-randomnetwork3', 'run': 'testrun2', 'network_name': 'testrun-randomnetwork3', 'total_num_training_games': 0, 'total_num_training_rows': 0, 'total_num_rating_games': Decimal('3'), 'total_rating_score': Decimal('1')}
{'network': 'testrun-randomnetwork4', 'run': 'testrun2', 'network_name': 'testrun-randomnetwork4', 'total_num_training_games': 3, 'total_num_training_rows': 0, 'total_num_rating_games': Decimal('3'), 'total_rating_score': Decimal('2')}
""")
        s = "\n"
        for obj in GameCountByUser.objects.all().order_by("username","run__name"):
            s += str(game_count_by_user_str(obj)) + "\n"
        assert(s == """
{'user': 'testuser', 'run': 'testrun', 'username': 'testuser', 'total_num_training_games': 3, 'total_num_training_rows': 0, 'total_num_rating_games': 0}
{'user': 'testuser', 'run': 'testrun2', 'username': 'testuser', 'total_num_training_games': 1, 'total_num_training_rows': 0, 'total_num_rating_games': 2}
{'user': 'testuser2', 'run': 'testrun', 'username': 'testuser2', 'total_num_training_games': 0, 'total_num_training_rows': 0, 'total_num_rating_games': 2}
{'user': 'testuser2', 'run': 'testrun2', 'username': 'testuser2', 'total_num_training_games': 2, 'total_num_training_rows': 0, 'total_num_rating_games': 1}
""")



