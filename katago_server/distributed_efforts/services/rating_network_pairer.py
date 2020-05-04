import numpy as np
import random
from math import log10, e, exp

from katago_server.games.models import TrainingGame
from katago_server.runs.models import Run
from katago_server.trainings.models import Network

class RatingNetworkPairerService:

    def __init__(self, run: Run):
        self.current_run = run

    def generate_task(self):
        """
        Generate a pairing of networks to play a rating game for a client task.

        :return: Tuple of (white_network,black_network)
        """
        if random.random() < self.current_run.rating_game_high_elo_probability:
            return self.generate_high_elo_game()
        else:
            return self.generate_high_uncertainty_game()

    def generate_high_elo_game(self):
        """
        In order to decrease the uncertainty of top network, we can chose to invest more on network having a chance to be the best ones.

        :return: Tuple of (white_network,black_network)
        """
        reference_network = Network.objects.select_one_of_the_best_with_uncertainty(self.current_run)
        opponent_network = self._choose_opponent(reference_network)
        if random.random() < 0.5:
            return (reference_network, opponent_network)
        else:
            return (opponent_network,reference_network)

    def generate_high_uncertainty_game(self):
        """
        In order to decrease the uncertainty of all network, we can look the one with biggest uncertainty.

        :return: Tuple of (white_network,black_network)
        """
        reference_network = Network.objects.select_one_of_the_more_uncertain(self.current_run)
        opponent_network = self._choose_opponent(reference_network)
        if random.random() < 0.5:
            return (reference_network, opponent_network)
        else:
            return (opponent_network,reference_network)

    def _choose_opponent(self, reference_network):
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
            Network.objects.exclude(pk=reference_network.pk).filter(run=self.current_run, log_gamma__lte=log_gamma_upper_bound, log_gamma__gte=log_gamma_lower_bound).all()
        )
        if len(nearby_networks) < 5:
            nearby_networks_a = Network.objects.filter(run=self.current_run, pk__lt=reference_network.pk).all()[:20]
            nearby_networks_b = Network.objects.filter(run=self.current_run, pk__gt=reference_network.pk).all()[:20]
            return np.random.choice(nearby_networks_a + nearby_networks_b)

        win_probability = np.asarray([1 / (1 + exp(opp_net.log_gamma - ref_net_log_gamma)) for opp_net in nearby_networks])
        shannon_entropy = -win_probability * np.log2(win_probability) - (1 - win_probability) * np.log2(1 - win_probability)

        return np.random.choice(nearby_networks, p=shannon_entropy / np.sum(shannon_entropy))
