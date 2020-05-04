from config import celery_app
from katago_server.games.models import RatingGame
from katago_server.runs.models import Run
from katago_server.trainings.models import Network
from katago_server.users.models import User


@celery_app.task()
def create_fake_initial():
    run, created = Run.objects.get_or_create(name="g170")

    if Network.objects.count() < 5:
        Network.objects.bulk_create(
            [
                Network(parent_network=None, model_file="https://d3dndmfyhecmj0.cloudfront.net/g170/neuralnets/g170-b6c96-s175395328-d26788732.bin.gz", run=run),
                Network(parent_network_id=1, model_file="https://d3dndmfyhecmj0.cloudfront.net/g170/neuralnets/g170-b6c96-s175395328-d26788732.bin.gz", run=run),
                Network(parent_network_id=2, model_file="https://d3dndmfyhecmj0.cloudfront.net/g170/neuralnets/g170-b6c96-s175395328-d26788732.bin.gz", run=run),
                Network(parent_network_id=3, model_file="https://d3dndmfyhecmj0.cloudfront.net/g170/neuralnets/g170-b6c96-s175395328-d26788732.bin.gz", run=run),
                Network(parent_network_id=4, model_file="https://d3dndmfyhecmj0.cloudfront.net/g170/neuralnets/g170-b6c96-s175395328-d26788732.bin.gz", run=run),
                Network(parent_network_id=5, model_file="https://d3dndmfyhecmj0.cloudfront.net/g170/neuralnets/g170-b6c96-s175395328-d26788732.bin.gz", run=run),
            ]
        )

    if RatingGame.objects.count() < 40:
        submitter = User.objects.first()

        RatingGame.objects.bulk_create(
            [
                # 1 <-> 2
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=1, black_network_id=2, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=1, black_network_id=2, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=1, black_network_id=2, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=1, black_network_id=2, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=1, black_network_id=2, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.WHITE, white_network_id=2, black_network_id=1, has_resigned=True
                ),
                RatingGame(submitted_by=submitter, run=run, result=RatingGame.GamesResult.DRAW, white_network_id=2, black_network_id=1),
                # 1 <-> 3
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=1, black_network_id=3, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=1, black_network_id=3, has_resigned=True
                ),
                RatingGame(submitted_by=submitter, run=run, result=RatingGame.GamesResult.DRAW, white_network_id=1, black_network_id=3),
                # 1 <-> 6
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=1, black_network_id=6, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.WHITE, white_network_id=1, black_network_id=6, has_resigned=True
                ),
                RatingGame(submitted_by=submitter, run=run, result=RatingGame.GamesResult.DRAW, white_network_id=1, black_network_id=6),
                # 2 <-> 4
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=2, black_network_id=4, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=2, black_network_id=4, has_resigned=True
                ),
                # 2 <-> 3
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=2, black_network_id=3, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=2, black_network_id=3, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=2, black_network_id=3, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.WHITE, white_network_id=2, black_network_id=3, has_resigned=True
                ),
                # 2 <-> 4
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=2, black_network_id=4, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=2, black_network_id=4, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=2, black_network_id=4, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.WHITE, white_network_id=2, black_network_id=4, has_resigned=True
                ),
                RatingGame(submitted_by=submitter, run=run, result=RatingGame.GamesResult.DRAW, white_network_id=2, black_network_id=4),
                # 2 <-> 5
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.WHITE, white_network_id=2, black_network_id=5, has_resigned=True
                ),
                RatingGame(submitted_by=submitter, run=run, result=RatingGame.GamesResult.DRAW, white_network_id=2, black_network_id=5),
                # 3 <-> 4
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=3, black_network_id=4, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=3, black_network_id=4, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=3, black_network_id=4, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=3, black_network_id=4, has_resigned=True
                ),
                # 3 <-> 5
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=3, black_network_id=5, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=3, black_network_id=5, has_resigned=True
                ),
                # 4 <-> 5
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=4, black_network_id=5, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.BLACK, white_network_id=4, black_network_id=5, has_resigned=True
                ),
                RatingGame(submitted_by=submitter, run=run, result=RatingGame.GamesResult.DRAW, white_network_id=4, black_network_id=5),
                RatingGame(submitted_by=submitter, run=run, result=RatingGame.GamesResult.DRAW, white_network_id=4, black_network_id=5),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True
                ),
                # 4 <-> 6
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True
                ),
                RatingGame(submitted_by=submitter, run=run, result=RatingGame.GamesResult.DRAW, white_network_id=4, black_network_id=5),
                RatingGame(submitted_by=submitter, run=run, result=RatingGame.GamesResult.DRAW, white_network_id=4, black_network_id=5),
                # 5 <-> 6
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.WHITE, white_network_id=4, black_network_id=5, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.DRAW, white_network_id=4, black_network_id=5, has_resigned=True
                ),
                RatingGame(
                    submitted_by=submitter, run=run, result=RatingGame.GamesResult.DRAW, white_network_id=4, black_network_id=5, has_resigned=True
                ),
            ]
        )
