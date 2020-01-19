from config import celery_app
from katago_server.games.models import RankingEstimationGame
from katago_server.trainings.models import Network
from katago_server.users.models import User


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
