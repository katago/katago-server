import random
import logging

from config import celery_app
from katago_server.distributed_efforts.models import RankingEstimationGameDistributedTask, RankingGameDistributedTaskGeneratorConfiguration
from katago_server.distributed_efforts.services.ranking_estimation_game_generator import RankingEstimationGameGeneratorService

logger = logging.getLogger(__name__)


@celery_app.task()
def schedule_ranking_estimation_game():
    config = RankingGameDistributedTaskGeneratorConfiguration.get_solo()

    ranking_game_generator = RankingEstimationGameGeneratorService()
    num_games = ranking_game_generator.how_many_games_to_generate()
    logger.info(f"generating {num_games} matches")

    new_ranking_game_tasks = []

    for _ in range(num_games):
        try:
            if random.random() < config.probability_high_elo:
                new_ranking_game_tasks.append(ranking_game_generator.generate_high_elo_game())
            else:
                new_ranking_game_tasks.append(ranking_game_generator.generate_high_uncertainty_game())
        except Exception as e:
            logger.warning(e)

    RankingEstimationGameDistributedTask.objects.bulk_create(new_ranking_game_tasks)
