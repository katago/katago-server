import logging
import random

from config import celery_app
from katago_server.games.models import TrainingGame
from katago_server.runs.models import Run
from katago_server.trainings.models import Network
from katago_server.users.models import User


logger = logging.getLogger(__name__)


@celery_app.task()
def create_fake_training_games():
    best_network = Network.objects.order_by("-log_gamma_lower_confidence").first()
    current_run = Run.objects.select_current()

    submitter = User.objects.first()
    games = [
        TrainingGame(
            submitted_by=submitter,
            black_network=best_network,
            white_network=best_network,
            result=TrainingGame.GamesResult.DRAW,
            sgf_file="https://google.fr",
            unpacked_file="https://google.fr",
            run=current_run
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
                run=current_run
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
                run=current_run
            )
        )

    TrainingGame.objects.bulk_create(games)
