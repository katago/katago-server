import random

import numpy as np
from math import log10, e, exp, log1p

from src.apps.runs.models import Run
from src.apps.trainings.models import Network


class RatingNetworkPairerService:
    def __init__(self, run: Run):
        self.current_run = run

    def generate_pairing(self):
        """
        Generate a pairing of networks to play a rating game for a client task.

        :return: Tuple of (white_network,black_network), or None if no pairing could be generated
        """

        high_elo_prob = self.current_run.rating_game_high_elo_probability
        high_uncertainty_prob = self.current_run.rating_game_high_uncertainty_probability
        low_data_prob = self.current_run.rating_game_low_data_probability

        total = high_elo_prob + high_uncertainty_prob + low_data_prob
        # If all three are zero, then equal-weight them
        if total <= 0:
            high_elo_prob = 1
            high_uncertainty_prob = 1
            low_data_prob = 1
            total = 3

        high_elo_prob /= total
        high_uncertainty_prob /= total
        low_data_prob /= total

        r = random.random()
        if r < high_elo_prob:
            return self.generate_high_elo_game()
        elif r < high_elo_prob + high_uncertainty_prob:
            return self.generate_high_uncertainty_game()
        else:
            return self.generate_low_data_game()

    def generate_high_elo_game(self):
        """
        In order to decrease the uncertainty of top network, we can chose to invest more on network having a chance to be the best ones.

        :return: Tuple of (white_network,black_network), or None if no pairing could be generated
        """
        reference_network = Network.objects.select_high_upper_confidence(self.current_run,for_rating_games=True)
        opponent_network = self._choose_opponent(reference_network)
        if reference_network is None or opponent_network is None:
            return None
        if random.random() < 0.5:
            return reference_network, opponent_network
        else:
            return opponent_network, reference_network

    def generate_high_uncertainty_game(self):
        """
        In order to decrease the uncertainty of all network, we can look the one with biggest uncertainty.

        :return: Tuple of (white_network,black_network), or None if no pairing could be generated
        """
        reference_network = Network.objects.select_high_uncertainty(self.current_run,for_rating_games=True)
        opponent_network = self._choose_opponent(reference_network)
        if reference_network is None or opponent_network is None:
            return None
        if random.random() < 0.5:
            return reference_network, opponent_network
        else:
            return opponent_network, reference_network

    def generate_low_data_game(self):
        """
        Try to generate a game on the network with the least actual games, regardless of modeled Elo or uncertainty.

        :return: Tuple of (white_network,black_network), or None if no pairing could be generated
        """
        reference_network = Network.objects.select_low_data(self.current_run,for_rating_games=True)
        opponent_network = self._choose_opponent(reference_network)
        if reference_network is None or opponent_network is None:
            return None
        if random.random() < 0.5:
            return reference_network, opponent_network
        else:
            return opponent_network, reference_network

    def _choose_opponent(self, reference_network):
        """
        Given a reference network, first preselect all networks in a fixed elo range.
        Then, for each network, calculate the win probability using log_gamma.
        Once we have all that, we look for a network close enough, selecting a network with probability proportional to the variance
        of the 0-1 game result.

        :param reference_network:
        :return: a network, chosen to be used as an opponent, or None if no distinct opponent could be found
        """
        if reference_network is None:
            return None

        # Vary the reference net's log gamma so that networks that are uncertain will play a greater variety of opponents
        # based on that uncertainty
        ref_net_log_gamma = reference_network.log_gamma + np.random.normal() * reference_network.log_gamma_uncertainty * self.current_run.rating_game_variability_scale

        log_gamma_search_range = 1200 / (400 * log10(e))  # Hardcoded window of 1200 Elo, we could dehardcode if needed in the future
        log_gamma_lower_bound = ref_net_log_gamma - log_gamma_search_range
        log_gamma_upper_bound = ref_net_log_gamma + log_gamma_search_range

        nearby_networks = (
            Network.objects.exclude(pk=reference_network.pk)
            .filter(run=self.current_run, rating_games_enabled=True, log_gamma__lte=log_gamma_upper_bound, log_gamma__gte=log_gamma_lower_bound,)
            .all()
        )
        if len(nearby_networks) < 4:
            nearby_weaker_networks = (
                Network.objects.exclude(pk=reference_network.pk)
                .filter(run=self.current_run, rating_games_enabled=True, log_gamma__lte=ref_net_log_gamma)
                .order_by("-log_gamma")
                .all()[:2]
            )
            nearby_stronger_networks = (
                Network.objects.exclude(pk=reference_network.pk)
                .filter(run=self.current_run, rating_games_enabled=True, log_gamma__gte=ref_net_log_gamma)
                .order_by("log_gamma")
                .all()[:2]
            )
            nearby_networks = list(nearby_weaker_networks) + list(nearby_stronger_networks)
            if len(nearby_networks) <= 0:
                return None
            return np.random.choice(nearby_networks)

        log_variances = [
            self._log_variance_of_gamma_difference((opp_net.log_gamma - ref_net_log_gamma) / self.current_run.rating_game_variability_scale) for opp_net in nearby_networks
        ]
        max_log_variance = max(log_variances)
        # Subtract out the max to make sure that we're near 0, for numerical stability
        log_variances = [ log_variance - max_log_variance for log_variance in log_variances ]
        variances = [ exp(log_variance) for log_variance in log_variances ]
        # print(log_variances)
        # print(variances)
        return np.random.choice(nearby_networks, p=variances / np.sum(variances))

    def _log_variance_of_gamma_difference(self, gamma_diff):
        # We would like to compute log(p * q) = log(p) + log(q)
        # where p = 1 / (1+exp(gamma_diff)) and q = 1 / (1+exp(-gamma_diff))
        return -self.log_one_plus_exp(gamma_diff) - self.log_one_plus_exp(-gamma_diff)

    # Computes log(1+exp(x)) in a numerically stable way
    def log_one_plus_exp(self, x):
        if x >= 40:
            return x
        return log1p(exp(x))

