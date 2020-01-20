import random

from config import celery_app
from katago_server.games.models import TrainingGame
from katago_server.trainings.models import Network
from katago_server.users.models import User


@celery_app.task()
def create_fake_training_games():
    best_network = Network.objects.order_by("-log_gamma_lower_confidence").first()

    submitter = User.objects.first()
    games = [
        TrainingGame(
            submitted_by=submitter,
            black_network=best_network,
            white_network=best_network,
            result=TrainingGame.GamesResult.DRAW,
            sgf_file="https://google.fr",
            unpacked_file="https://google.fr",
        )
    ]

    if random.random() < 0.2:
        games.append(
            TrainingGame(
                submitted_by=submitter,
                black_network=best_network,
                white_network=best_network,
                result=TrainingGame.GamesResult.DRAW,
                sgf_file="https://google.fr",
                unpacked_file="https://google.fr",
            )
        )

    if random.random() < 0.1:
        games.append(
            TrainingGame(
                submitted_by=submitter,
                black_network=best_network,
                white_network=best_network,
                result=TrainingGame.GamesResult.DRAW,
                sgf_file="https://google.fr",
                unpacked_file="https://google.fr",
            )
        )

    TrainingGame.objects.bulk_create(games)
