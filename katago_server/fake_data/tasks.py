import random

from celery.signals import worker_ready
import logging

from config import celery_app
from katago_server.distributed_efforts.models import RankingEstimationGameDistributedTask
from katago_server.games.models import RankingEstimationGame, TrainingGame
from katago_server.trainings.models import Network
from katago_server.users.models import User

logger = logging.getLogger(__name__)


@worker_ready.connect
def on_worker_ready(sender=None, conf=None, **kwargs):
    create_fake_initial.delay()


@celery_app.task()
def create_fake_initial():
    if not Network.objects.count() >= 5:
        Network.objects.bulk_create([
            Network(nb_blocks=6, nb_channels=125, parent_network=None, model_file="http://google.fr"),
            Network(nb_blocks=6, nb_channels=125, parent_network_id=1, model_file="http://google.fr"),
            Network(nb_blocks=6, nb_channels=125, parent_network_id=2, model_file="http://google.fr"),
            Network(nb_blocks=6, nb_channels=125, parent_network_id=3, model_file="http://google.fr"),
            Network(nb_blocks=6, nb_channels=125, parent_network_id=4, model_file="http://google.fr"),
            Network(nb_blocks=6, nb_channels=125, parent_network_id=5, model_file="http://google.fr"),
        ])

    if not RankingEstimationGame.objects.count() >= 40:
        submitter = User.objects.first()

        RankingEstimationGame.objects.bulk_create([
            # 1 <-> 2
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=1, black_network_id=2, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=1, black_network_id=2, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=1, black_network_id=2, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=1, black_network_id=2, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=1, black_network_id=2, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.WHITE, white_network_id=2, black_network_id=1, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.DRAW,  white_network_id=2, black_network_id=1),
            # 1 <-> 3
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=1, black_network_id=3, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=1, black_network_id=3, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.DRAW,  white_network_id=1, black_network_id=3),
            # 1 <-> 6
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=1, black_network_id=6, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.WHITE, white_network_id=1, black_network_id=6, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.DRAW,  white_network_id=1, black_network_id=6),
            # 2 <-> 4
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=2, black_network_id=4, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=2, black_network_id=4, has_resigned=True),
            # 2 <-> 3
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=2, black_network_id=3, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=2, black_network_id=3, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=2, black_network_id=3, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.WHITE, white_network_id=2, black_network_id=3, has_resigned=True),
            # 2 <-> 4
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=2, black_network_id=4, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=2, black_network_id=4, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=2, black_network_id=4, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.WHITE, white_network_id=2, black_network_id=4, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.DRAW,  white_network_id=2, black_network_id=4),
            # 2 <-> 5
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.WHITE, white_network_id=2, black_network_id=5, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.DRAW,  white_network_id=2, black_network_id=5),
            # 3 <-> 4
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=3, black_network_id=4, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=3, black_network_id=4, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=3, black_network_id=4, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=3, black_network_id=4, has_resigned=True),
            # 3 <-> 5
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=3, black_network_id=5, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=3, black_network_id=5, has_resigned=True),
            # 4 <-> 5
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=4, black_network_id=5, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.BLACK, white_network_id=4, black_network_id=5, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.DRAW,  white_network_id=4, black_network_id=5),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.DRAW,  white_network_id=4, black_network_id=5),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True),
            # 4 <-> 6
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.DRAW,  white_network_id=4, black_network_id=5),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.DRAW,  white_network_id=4, black_network_id=5),
            # 5 <-> 6
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.DRAW,  white_network_id=4, black_network_id=5, has_resigned=True),
            RankingEstimationGame(submitted_by=submitter, result=RankingEstimationGame.GamesResult.DRAW,  white_network_id=4, black_network_id=5, has_resigned=True),
        ])


@celery_app.task()
def create_fake_additional_network():
    last_network = Network.objects.last()

    new_net = Network(nb_blocks=6, nb_channels=125, parent_network_id=last_network.id, model_file="http://google.fr")
    new_net.save()


# noinspection DuplicatedCode
@celery_app.task()
def create_fake_ranking_estimation_games():
    ranking_estimation_games_tasks = RankingEstimationGameDistributedTask.objects.filter(status=RankingEstimationGameDistributedTask.Status.UNASSIGNED).all()

    submitter = User.objects.first()

    games = []
    tasks = []

    for task in ranking_estimation_games_tasks:
        white_network = task.white_network
        black_network = task.black_network

        diff = abs(black_network.pk - white_network.pk)

        PROB_WIN = 0
        PROB_LOOSE = 0
        PROB_DRAW = 0.95

        if diff < 3:
            PROB_WIN = 0.6
            PROB_LOOSE = 0.7
        elif diff < 5:
            PROB_WIN = 0.8
            PROB_LOOSE = 0.5
        elif diff < 8:
            PROB_WIN = 0.95
            PROB_LOOSE = 0.3
        elif diff < 13:
            PROB_WIN = 0.999
            PROB_LOOSE = 0.2

        if black_network.pk < white_network.pk:
            if random.random() < PROB_WIN:
                games.append(RankingEstimationGame(submitted_by=submitter, white_network=white_network, black_network=black_network, result=RankingEstimationGame.GamesResult.WHITE, has_resigned=True))
                task.status = RankingEstimationGameDistributedTask.Status.DONE
                tasks.append(task)
                continue
            if random.random() < PROB_LOOSE:
                games.append(RankingEstimationGame(submitted_by=submitter, white_network=white_network, black_network=black_network, result=RankingEstimationGame.GamesResult.BLACK, has_resigned=True))
                task.status = RankingEstimationGameDistributedTask.Status.DONE
                tasks.append(task)
                continue
            if random.random() < PROB_DRAW:
                games.append(RankingEstimationGame(submitted_by=submitter, white_network=white_network, black_network=black_network, result=RankingEstimationGame.GamesResult.DRAW))
                task.status = RankingEstimationGameDistributedTask.Status.DONE
                tasks.append(task)
                continue
        if white_network.pk < black_network.pk:
            if random.random() < PROB_WIN:
                games.append(RankingEstimationGame(submitted_by=submitter, white_network=white_network, black_network=black_network, result=RankingEstimationGame.GamesResult.BLACK, has_resigned=True))
                task.status = RankingEstimationGameDistributedTask.Status.DONE
                tasks.append(task)
                continue
            if random.random() < PROB_LOOSE:
                games.append(RankingEstimationGame(submitted_by=submitter, white_network=white_network, black_network=black_network, result=RankingEstimationGame.GamesResult.WHITE, has_resigned=True))
                task.status = RankingEstimationGameDistributedTask.Status.DONE
                tasks.append(task)
                continue
            if random.random() < PROB_DRAW:
                games.append(RankingEstimationGame(submitted_by=submitter, white_network=white_network, black_network=black_network, result=RankingEstimationGame.GamesResult.DRAW))
                task.status = RankingEstimationGameDistributedTask.Status.DONE
                tasks.append(task)
                continue

    RankingEstimationGame.objects.bulk_create(games)
    RankingEstimationGameDistributedTask.objects.bulk_update(tasks, ['status'])


@celery_app.task()
def create_fake_training_games():
    best_network = Network.objects.order_by("-log_gamma_lower_confidence").first()

    submitter = User.objects.first()
    games = [
        TrainingGame(submitted_by=submitter, black_network=best_network, white_network=best_network, result=TrainingGame.GamesResult.DRAW, sgf_file="https://google.fr", unpacked_file="https://google.fr")
    ]

    if random.random() < 0.2:
        games.append(TrainingGame(submitted_by=submitter, black_network=best_network, white_network=best_network, result=TrainingGame.GamesResult.DRAW, sgf_file="https://google.fr", unpacked_file="https://google.fr"))

    if random.random() < 0.1:
        games.append(TrainingGame(submitted_by=submitter, black_network=best_network, white_network=best_network, result=TrainingGame.GamesResult.DRAW, sgf_file="https://google.fr", unpacked_file="https://google.fr"))

    TrainingGame.objects.bulk_create(games)
