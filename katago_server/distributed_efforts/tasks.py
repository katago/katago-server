import logging
import random
from datetime import timedelta
from math import log10, e, exp

import numpy
import pandas
import scipy.stats
from django.db.models import Count
from django.utils import timezone
from django_celery_beat.models import PeriodicTask
from django_pandas.io import read_frame

from config import celery_app
from katago_server.distributed_efforts.models import RankingEstimationGameDistributedTask, RankingGameGeneratorConfiguration
from katago_server.games.models import TrainingGame, RankingEstimationGame
from katago_server.trainings.models import Network

logger = logging.getLogger(__name__)


def _get_schedule_timedelta():
    periodic_task = PeriodicTask.objects.filter(task="katago_server.distributed_efforts.tasks.schedule_ranking_estimation_game").get()
    interval_obj = periodic_task.interval
    interval_timedelta = timedelta(**{interval_obj.period: interval_obj.every})
    return interval_timedelta


def _get_how_much_ranking_game_task_to_generate():
    number_of_training_in_interval = TrainingGame.objects.filter(created_at__gte=timezone.now() - _get_schedule_timedelta()).count()
    return round(number_of_training_in_interval * RankingGameGeneratorConfiguration.get_solo().ratio)


def _random_weighted_choice(array):
    probability_to_be_picked = scipy.stats.expon.pdf([index for index, _ in enumerate(array)], loc=0, scale=2)
    probability_to_be_picked /= numpy.sum(probability_to_be_picked)
    return numpy.random.choice(array, p=probability_to_be_picked)


def _choose_opponent(reference_network):
    reference_network_log_gamma = reference_network.log_gamma
    lower_bound = reference_network_log_gamma - 600 / (400 * log10(e))
    upper_bound = reference_network_log_gamma + 600 / (400 * log10(e))

    nearby_networks = Network.objects.exclude(pk=reference_network.pk).filter(log_gamma__lte=upper_bound, log_gamma__gte=lower_bound).all()
    if len(nearby_networks) < 1:
        # TODO
        pass
    win_probability = numpy.asarray([1 / (1 + exp(opponent_network.log_gamma - reference_network_log_gamma)) for opponent_network in nearby_networks])
    entropy = -win_probability * numpy.log2(win_probability) - (1 - win_probability) * numpy.log2(1 - win_probability)

    return numpy.random.choice(nearby_networks, p=entropy/numpy.sum(entropy))


# def _generate_high_elo_ranking_estimation_games_task():
    #  more_uncertain_networks = Network.objects.order_by("-log_gamma_uncertainty").values_list("id", flat=True)[:nb_games * 2]
    #
    #     total_games_aggregate = Count('id')
    #
    #     tournament_result_white_qs = RankingEstimationGame.objects.filter(white_network__in=more_uncertain_networks).values('white_network__pk').annotate(total_games_white=total_games_aggregate)
    #     tournament_result_white = read_frame(tournament_result_white_qs, fieldnames=['white_network__pk', 'total_games_white'])
    #     tournament_result_white = tournament_result_white.rename(columns={'white_network__pk': 'reference_network'}, errors="raise")
    #
    #     tournament_result_black_qs = RankingEstimationGame.objects.filter(black_network__in=more_uncertain_networks).values('black_network__pk').annotate(total_games_black=total_games_aggregate)
    #     tournament_result_black = read_frame(tournament_result_black_qs, fieldnames=['black_network__pk', 'total_games_black'])
    #     tournament_result_black = tournament_result_black.rename(columns={'black_network__pk': 'reference_network'}, errors="raise")
    #
    #     tournament_result = pandas.merge(tournament_result_white, tournament_result_black, how='outer', on=['reference_network'])
    #     tournament_result = tournament_result.fillna(0)
    #
    #     tournament_result.group_by(["reference_network"]).sum()
    #
    #     logger.info(tournament_result)
    #
    #     # return _generate_ranking_estimation_game_task(reference_network, opponent_network)
def _generate_high_elo_ranking_estimation_game_task():
    best_networks = Network.objects.order_by("-log_gamma_upper_confidence")[:10]
    reference_network = _random_weighted_choice(best_networks)
    opponent_network = _choose_opponent(reference_network)
    return _generate_ranking_estimation_game_task(reference_network, opponent_network)


def _generate_high_uncertainty_ranking_estimation_game_task():
    best_networks = Network.objects.order_by("-log_gamma_uncertainty")[:10]
    reference_network = _random_weighted_choice(best_networks)
    opponent_network = _choose_opponent(reference_network)
    return _generate_ranking_estimation_game_task(reference_network, opponent_network)


def _generate_ranking_estimation_game_task(reference_network, opponent_network):
    if random.random() < 0.5:
        return RankingEstimationGameDistributedTask(white_network=reference_network, black_network=opponent_network)
    else:
        return RankingEstimationGameDistributedTask(white_network=opponent_network, black_network=reference_network)


@celery_app.task()
def schedule_ranking_estimation_game():
    num_games = _get_how_much_ranking_game_task_to_generate()

    new_ranking_game_tasks = []
    # high_uncertainty_games_to_generate = 0
    for _ in range(num_games):
        if random.random() < RankingGameGeneratorConfiguration.get_solo().probability_high_elo:
            new_ranking_game_tasks.append(_generate_high_elo_ranking_estimation_game_task())
        else:
            # high_uncertainty_games_to_generate += 1
            new_ranking_game_tasks.append(_generate_high_uncertainty_ranking_estimation_game_task())

    # new_ranking_game_tasks.append(_generate_high_uncertainty_ranking_estimation_games_task(high_uncertainty_games_to_generate))

    RankingEstimationGameDistributedTask.objects.bulk_create(new_ranking_game_tasks)
