import random

from config import celery_app
from katago_server.games.models import RatingGame
from katago_server.runs.models import Run
from katago_server.users.models import User


# @celery_app.task()
# def create_fake_ranking_estimation_games():
#     ranking_estimation_games_tasks = RatingGameDistributedTask.objects.filter(
#         status=RatingGameDistributedTask.Status.UNASSIGNED
#     ).all()

#     current_run = Run.objects.last()
#     submitter = User.objects.first()

#     games = []
#     tasks = []

#     for task in ranking_estimation_games_tasks:
#         white_network = task.white_network
#         black_network = task.black_network

#         diff = abs(black_network.pk - white_network.pk)

#         PROB_WIN = 0
#         PROB_LOOSE = 0
#         PROB_DRAW = 0.95

#         if diff < 3:
#             PROB_WIN = 0.6
#             PROB_LOOSE = 0.7
#         elif diff < 5:
#             PROB_WIN = 0.8
#             PROB_LOOSE = 0.5
#         elif diff < 8:
#             PROB_WIN = 0.90
#             PROB_LOOSE = 0.3
#         elif diff < 13:
#             PROB_WIN = 0.95
#             PROB_LOOSE = 0.2
#         else:
#             PROB_WIN = 0.95
#             PROB_LOOSE = 0.1

#         if black_network.pk < white_network.pk:
#             if random.random() < PROB_WIN:
#                 games.append(
#                     RatingGame(
#                         submitted_by=submitter,
#                         white_network=white_network,
#                         black_network=black_network,
#                         result=RatingGame.GamesResult.WHITE,
#                         has_resigned=True,
#                         run=current_run
#                     )
#                 )
#                 task.run = current_run
#                 task.status = RatingGameDistributedTask.Status.DONE
#                 tasks.append(task)
#                 continue
#             if random.random() < PROB_LOOSE:
#                 games.append(
#                     RatingGame(
#                         submitted_by=submitter,
#                         white_network=white_network,
#                         black_network=black_network,
#                         result=RatingGame.GamesResult.BLACK,
#                         has_resigned=True,
#                         run=current_run
#                     )
#                 )
#                 task.run = current_run
#                 task.status = RatingGameDistributedTask.Status.DONE
#                 tasks.append(task)
#                 continue
#             if random.random() < PROB_DRAW:
#                 games.append(
#                     RatingGame(
#                         submitted_by=submitter,
#                         white_network=white_network,
#                         black_network=black_network,
#                         result=RatingGame.GamesResult.DRAW,
#                         run=current_run
#                     )
#                 )
#                 task.run = current_run
#                 task.status = RatingGameDistributedTask.Status.DONE
#                 tasks.append(task)
#                 continue

#         if white_network.pk < black_network.pk:
#             if random.random() < PROB_WIN:
#                 games.append(
#                     RatingGame(
#                         submitted_by=submitter,
#                         white_network=white_network,
#                         black_network=black_network,
#                         result=RatingGame.GamesResult.BLACK,
#                         has_resigned=True,
#                         run=current_run
#                     )
#                 )
#                 task.run = current_run
#                 task.status = RatingGameDistributedTask.Status.DONE
#                 tasks.append(task)
#                 continue
#             if random.random() < PROB_LOOSE:
#                 games.append(
#                     RatingGame(
#                         submitted_by=submitter,
#                         white_network=white_network,
#                         black_network=black_network,
#                         result=RatingGame.GamesResult.WHITE,
#                         has_resigned=True,
#                         run=current_run
#                     )
#                 )
#                 task.run = current_run
#                 task.status = RatingGameDistributedTask.Status.DONE
#                 tasks.append(task)
#                 continue
#             if random.random() < PROB_DRAW:
#                 games.append(
#                     RatingGame(
#                         submitted_by=submitter,
#                         white_network=white_network,
#                         black_network=black_network,
#                         result=RatingGame.GamesResult.DRAW,
#                         run=current_run
#                     )
#                 )
#                 task.run = current_run
#                 task.status = RatingGameDistributedTask.Status.DONE
#                 tasks.append(task)
#                 continue

#     RatingGame.objects.bulk_create(games)
#     RatingGameDistributedTask.objects.bulk_update(tasks, ["status"])
