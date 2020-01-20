from math import log10, e, exp

import numpy as np
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from katago_server.distributed_efforts.models import RankingGameDistributedTaskGeneratorConfiguration, RankingEstimationGameDistributedTask
from katago_server.games.models import TrainingGame
from datetime import timedelta

from katago_server.trainings.models import Network


class RankingEstimationGameGeneratorService:
    TASK_NAME = "katago_server.distributed_efforts.tasks.schedule_ranking_estimation_game.schedule_ranking_estimation_game"

    def __init__(self):
        self.config = RankingGameDistributedTaskGeneratorConfiguration.get_solo()

    def how_many_games_to_generate(self):
        """
        This check how often the scheduling of match is executed: let's call this "delta_t"
        Based on this delta, and how much training game have been generated, it schedules "X" games so a given ratio is respected.
        (eg we want 1/10 of games to be ranking estimation)
        The ratio is configurable in db

        :return: a number of game to generate
        """
        periodic_task = PeriodicTask.objects.filter(task=self.TASK_NAME).get()
        interval_timedelta = timedelta(**{periodic_task.interval.period: periodic_task.interval.every})
        number_of_training_in_interval = TrainingGame.objects.filter(created_at__gte=timezone.now() - interval_timedelta).count()
        return round(number_of_training_in_interval * self.config.ratio)

    def generate_high_elo_game(self):
        """
        In order to decrease the uncertainty of top network, we can chose to invest more on network having a chance to be the best ones.

        :return:
        """
        reference_network = Network.objects.select_one_of_the_best_with_uncertainty()
        opponent_network = self._choose_opponent(reference_network)
        return RankingEstimationGameDistributedTask.create_with_random_color(reference_network, opponent_network)

    def generate_high_uncertainty_game(self):
        """
        In order to decrease the uncertainty of all network, we can look the one with biggest uncertainty.

        :return:
        """
        reference_network = Network.objects.select_one_of_the_more_uncertain()
        opponent_network = self._choose_opponent(reference_network)
        return RankingEstimationGameDistributedTask.create_with_random_color(reference_network, opponent_network)

    @staticmethod
    def _choose_opponent(reference_network):
        """
        Given a reference network, first preselect all networks in a fixed elo range.
        Then, for each network, calculate the win probability using log_gamma.
        Once we have all that, we look for a network close enough, by applying shannon entropy: https://imgur.com/v9Q4By7

        :param reference_network:
        :return: a network, chosen to be used as an opponent
        """
        ref_net_log_gamma = reference_network.log_gamma  # TODO should I use log_gamma or log_gamma + uncertainty ?

        log_gamma_search_range = 1200 / (400 * log10(e))  # TODO: should I make this configurable
        log_gamma_lower_bound = ref_net_log_gamma - log_gamma_search_range
        log_gamma_upper_bound = ref_net_log_gamma + log_gamma_search_range

        nearby_networks = (
            Network.objects.exclude(pk=reference_network.pk).filter(log_gamma__lte=log_gamma_upper_bound, log_gamma__gte=log_gamma_lower_bound).all()
        )
        if len(nearby_networks) < 5:
            nearby_networks_a = Network.objects.filter(pk__lt=reference_network.pk).all()[:20]
            nearby_networks_b = Network.objects.filter(pk__gt=reference_network.pk).all()[:20]
            return np.random.choice(nearby_networks_a + nearby_networks_b)

        win_probability = np.asarray([1 / (1 + exp(opp_net.log_gamma - ref_net_log_gamma)) for opp_net in nearby_networks])
        shannon_entropy = -win_probability * np.log2(win_probability) - (1 - win_probability) * np.log2(1 - win_probability)

        return np.random.choice(nearby_networks, p=shannon_entropy / np.sum(shannon_entropy))
