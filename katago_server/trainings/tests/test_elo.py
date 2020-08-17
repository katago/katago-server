import pytest
import math

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from katago_server.runs.models import Run
from katago_server.games.models import RatingGame
from katago_server.trainings.models import Network
from katago_server.trainings.tasks import update_bayesian_rating

pytestmark = pytest.mark.django_db

User = get_user_model()

fake_sha256 = "12341234abcdabcd56785678abcdabcd12341234abcdabcd56785678abcdabcd"


class TestEloLoneNetwork:

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

    def teardown_method(self):
        self.n1.delete()
        self.r1.delete()

    def test_elos(self):
        update_bayesian_rating()
        self.n1.refresh_from_db()
        assert(self.n1.log_gamma == 0)
        assert(self.n1.log_gamma_uncertainty == 0)


class TestEloTwoNetworksNoGames:

    def setup_method(self):
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.0,
            status="Active",
            elo_number_of_iterations = 50,
            virtual_draw_strength = 25.0,
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
            parent_network=self.n1,
        )

    def teardown_method(self):
        self.n2.delete()
        self.n1.delete()
        self.r1.delete()

    def test_elos(self):
        update_bayesian_rating()
        self.n1.refresh_from_db()
        self.n2.refresh_from_db()
        assert(self.n1.log_gamma == 0)
        assert(self.n2.log_gamma == 0)
        assert(self.n1.log_gamma_uncertainty == pytest.approx(0.4))
        assert(self.n2.log_gamma_uncertainty == pytest.approx(0.4))


def make_games(run,user,n1,n2,n1wins,n2wins,draws,noresults):
    black = RatingGame.GamesResult.BLACK
    white = RatingGame.GamesResult.WHITE
    draw = RatingGame.GamesResult.DRAW
    noresult = RatingGame.GamesResult.NO_RESULT
    games = []
    for i in range(n1wins):
        games.append(RatingGame(
            run=run,
            submitted_by=user,
            winner=black,
            black_network=n1,
            white_network=n2,
        ))
    for i in range(n2wins):
        games.append(RatingGame(
            run=run,
            submitted_by=user,
            winner=white,
            black_network=n1,
            white_network=n2,
        ))
    for i in range(draws):
        games.append(RatingGame(
            run=run,
            submitted_by=user,
            winner=draw,
            black_network=n1,
            white_network=n2,
        ))
    for i in range(noresults):
        games.append(RatingGame(
            run=run,
            submitted_by=user,
            winner=noresult,
            black_network=n1,
            white_network=n2,
        ))
    return games

class TestEloTwoNetworksSomeGames:

    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
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
        self.n2 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork2",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
            parent_network=self.n1,
        )

        # With 4 losses, 10 wins, and 4 virtual draws, that's effectively
        # 12 wins vs 6 losses.
        # This is 2:1 winning odds, so gamma = 2/1 = 2, therefore loggamma = ln(2).
        # Also, if you work it out, you get that the precision per game is
        # 1/(sqrt2 + (1/sqrt2))^2 = 1/(2+2+0.5) 1/4.5, which with 18 games comes out to exactly precision 4,
        # and therefore uncertainty 0.5.
        self.games = make_games(self.r1,self.u1,self.n1,self.n2,4,10,0,0)
        RatingGame.objects.bulk_create(self.games)

    def teardown_method(self):
        for game in self.games:
            game.delete()
        self.n2.delete()
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_elos(self):
        update_bayesian_rating()
        self.n1.refresh_from_db()
        self.n2.refresh_from_db()
        assert(self.n1.log_gamma == pytest.approx(0.0))
        assert(self.n2.log_gamma == pytest.approx(math.log(2)))
        assert(self.n1.log_gamma_uncertainty == pytest.approx(0.5))
        assert(self.n2.log_gamma_uncertainty == pytest.approx(0.5))

class TestEloTwoNetworksSomeGamesWithDraws:

    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
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
        self.n2 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork2",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
            parent_network=self.n1,
        )

        # With 8 losses, 32 wins, and 4 virtual draws and 4 fake draws, that's effectively
        # 36 wins vs 12 losses.
        # This is 3:1 winning odds, so gamma = 3/1 = 3, therefore loggamma = ln(3).
        # Also, if you work it out, you get that the precision per game is
        # 1/(sqrt3 + (1/sqrt3))^2 = 1/(3+2+1/3) 1/(16/3) = 3/16, which with 48 games comes out to
        # precision 9, and therefore uncertainty 1/3
        self.games = make_games(self.r1,self.u1,self.n1,self.n2,8,32,3,1)
        RatingGame.objects.bulk_create(self.games)

    def teardown_method(self):
        for game in self.games:
            game.delete()
        self.n2.delete()
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_elos(self):
        update_bayesian_rating()
        self.n1.refresh_from_db()
        self.n2.refresh_from_db()
        assert(self.n1.log_gamma == pytest.approx(0.0))
        assert(self.n2.log_gamma == pytest.approx(math.log(3)))
        assert(self.n1.log_gamma_uncertainty == pytest.approx(1/3))
        assert(self.n2.log_gamma_uncertainty == pytest.approx(1/3))


class TestEloChain:
    """Chain of networks each one beating the previous one by 2:1, and the last one by 5:1"""

    def setup_method(self):
        self.u1 = User.objects.create_user(username="test", password="test")
        self.r1 = Run.objects.create(
            name="testrun",
            rating_game_probability=0.0,
            status="Active",
            elo_number_of_iterations = 100,
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
        self.n2 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork2",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
            parent_network=self.n1,
        )
        self.n3 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork3",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
            parent_network=self.n1,
        )
        self.n4 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork4",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
            parent_network=self.n3,
        )
        self.n5 = Network.objects.create(
            run=self.r1,
            name="testrun-randomnetwork5",
            model_file="",
            model_file_bytes=0,
            model_file_sha256=fake_sha256,
            log_gamma=0,
            is_random=True,
            parent_network=self.n4,
        )

        # For the last game set, which is a 40:8 ratio, the uncertainty:
        # 1/(sqrt5 + (1/sqrt5))^2 = 1/(5+2+1/5) 1/(36/5) = 5/36, which with 48 games comes out to
        # precision 20/3, and therefore uncertainty sqrt(3/20)
        self.games = []
        self.games.extend(make_games(self.r1,self.u1,self.n1,self.n2,10,4,0,0)) # 18 games with prior
        self.games.extend(make_games(self.r1,self.u1,self.n1,self.n3,0,6,5,3))  # 18 games with prior
        self.games.extend(make_games(self.r1,self.u1,self.n3,self.n4,5,17,3,7)) # 36 games with prior
        self.games.extend(make_games(self.r1,self.u1,self.n4,self.n5,6,38,0,0)) # 48 games with prior
        RatingGame.objects.bulk_create(self.games)

    def teardown_method(self):
        for game in self.games:
            game.delete()
        self.n5.delete()
        self.n4.delete()
        self.n3.delete()
        self.n2.delete()
        self.n1.delete()
        self.r1.delete()
        self.u1.delete()

    def test_elos(self):
        update_bayesian_rating()
        self.n1.refresh_from_db()
        self.n2.refresh_from_db()
        self.n3.refresh_from_db()
        self.n4.refresh_from_db()
        self.n5.refresh_from_db()
        assert(self.n1.log_gamma == pytest.approx(0.0))
        assert(self.n2.log_gamma == pytest.approx(-math.log(2)))
        assert(self.n3.log_gamma == pytest.approx(math.log(2)))
        assert(self.n4.log_gamma == pytest.approx(math.log(2)*2))
        assert(self.n5.log_gamma == pytest.approx(math.log(2)*2+math.log(5)))
        assert(self.n1.log_gamma_uncertainty == pytest.approx(0.5/math.sqrt(2)))
        assert(self.n2.log_gamma_uncertainty == pytest.approx(0.5))
        assert(self.n3.log_gamma_uncertainty == pytest.approx(math.sqrt(1/(4+8))))
        assert(self.n4.log_gamma_uncertainty == pytest.approx(math.sqrt(1/(20/3 + 8))))
        assert(self.n5.log_gamma_uncertainty == pytest.approx(math.sqrt(3/20)))
