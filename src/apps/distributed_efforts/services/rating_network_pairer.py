import random

import numpy as np
from math import log10, e, exp

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
        if random.random() < self.current_run.rating_game_high_elo_probability:
            return self.generate_high_elo_game()
        else:
            return self.generate_high_uncertainty_game()

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

    def _choose_opponent(self, reference_network):
        """
        Given a reference network, first preselect all networks in a fixed elo range.
        Then, for each network, calculate the win probability using log_gamma.
        Once we have all that, we look for a network close enough, by applying shannon entropy: https://imgur.com/v9Q4By7

        :param reference_network:
        :return: a network, chosen to be used as an opponent, or None if no distinct opponent could be found
        """
        if reference_network is None:
            return None

        # Vary the reference net's log gamma so that networks that are uncertain will play a greater variety of opponents
        # based on that uncertainty
        ref_net_log_gamma = reference_network.log_gamma + np.random.normal() * reference_network.log_gamma_uncertainty

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

        win_probability = np.asarray([
            1 / (1 + exp((opp_net.log_gamma - ref_net_log_gamma) / self.current_run.rating_game_entropy_scale)) for opp_net in nearby_networks
        ])
        shannon_entropy = -win_probability * np.log2(win_probability) - (1 - win_probability) * np.log2(1 - win_probability)

        return np.random.choice(nearby_networks, p=shannon_entropy / np.sum(shannon_entropy))
