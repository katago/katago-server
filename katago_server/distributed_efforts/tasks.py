import logging
import random
from math import log10, e, exp

import numpy
import scipy.stats
from celery.signals import worker_ready
from django.utils import timezone

from config import celery_app
from katago_server.distributed_efforts.models import RankingEstimationGameDistributedTask
from katago_server.games.models import TrainingGame
from katago_server.trainings.models import Network

logger = logging.getLogger(__name__)

TIME_DELTA = 600  # generate a set of match every 600 seconds
RANKING_GAMES_RATIO = 0.1
MIN_RANKING_GAMES = 5
PROB_HIGH_ELO_GAME = 0.4


def _random_choice_normal(array):
    probability_to_be_picked = scipy.stats.norm.pdf([index for index, _ in enumerate(array)], loc=0, scale=2)
    probability_to_be_picked /= numpy.sum(probability_to_be_picked)
    return numpy.random.choice(array, p=probability_to_be_picked)


def _choose_opponent(reference_network):
    reference_network_log_gamma = reference_network.log_gamma
    lower_bound = reference_network_log_gamma - 600 / (400 * log10(e))
    upper_bound = reference_network_log_gamma + 600 / (400 * log10(e))

    nearby_networks = Network.objects.exclude(pk=reference_network.pk).filter(log_gamma__lte=upper_bound, log_gamma__gte=lower_bound).all()
    if len(nearby_networks) < 10:
        # TODO
        pass
    win_probability = numpy.asarray([1 / (1 + exp(opponent_network.log_gamma - reference_network_log_gamma)) for opponent_network in nearby_networks])
    entropy = -win_probability * numpy.log2(win_probability) - (1 - win_probability) * numpy.log2(1 - win_probability)

    return numpy.random.choice(nearby_networks, p=entropy/numpy.sum(entropy))


def _get_how_much_ranking_game_task_to_generate():
    number_of_training_in_interval = TrainingGame.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(seconds=TIME_DELTA)).count()
    return max(round(number_of_training_in_interval * RANKING_GAMES_RATIO), MIN_RANKING_GAMES)


def _generate_high_elo_ranking_estimation_game_task():
    best_networks = Network.objects.order_by("-log_gamma_upper_confidence")[:10]
    reference_network = _random_choice_normal(best_networks)
    opponent_network = _choose_opponent(reference_network)
    return _generate_ranking_estimation_game_task(reference_network, opponent_network)


def _generate_high_uncertainty_ranking_estimation_game_task():
    best_networks = Network.objects.order_by("-log_gamma_uncertainty")[:10]
    reference_network = _random_choice_normal(best_networks)
    opponent_network = _choose_opponent(reference_network)
    return _generate_ranking_estimation_game_task(reference_network, opponent_network)


def _generate_ranking_estimation_game_task(reference_network, opponent_network):
    if random.random() < 0.5:
        return RankingEstimationGameDistributedTask(white_network=reference_network, black_network=opponent_network)
    else:
        return RankingEstimationGameDistributedTask(white_network=opponent_network, black_network=reference_network)


@celery_app.task(bind=True)
def schedule_ranking_estimation_game(network_id):
    num_games = _get_how_much_ranking_game_task_to_generate()

    new_ranking_game_tasks = []
    for _ in range(num_games):
        if random.random() < PROB_HIGH_ELO_GAME or True:
            new_ranking_game_tasks.append(_generate_high_elo_ranking_estimation_game_task())
        else:
            new_ranking_game_tasks.append(_generate_high_uncertainty_ranking_estimation_game_task())

    RankingEstimationGameDistributedTask.objects.bulk_create(new_ranking_game_tasks)
