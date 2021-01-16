import logging

import math
import numpy as np
import scipy.stats
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import QuerySet

from src.apps.runs.models import Run

logger = logging.getLogger(__name__)


def random_weighted_choice(networks):
    probability_to_be_picked = scipy.stats.expon.pdf([index for index, _ in enumerate(networks)], loc=0, scale=2)
    probability_to_be_picked /= np.sum(probability_to_be_picked)
    return np.random.choice(networks, p=probability_to_be_picked)


class NetworkQuerySet(QuerySet):
    """
    NetworkQuerySet helps selecting network that are either good or have a big uncertainty in their rating
    network_delay indicates to only select networks older than this many seconds
    """

    def select_networks_for_run(self, run: Run, for_training_games=False, for_rating_games=False, network_delay=None):
        if for_training_games:
            if for_rating_games:
                filtered = self.filter(run=run, training_games_enabled=True, rating_games_enabled=True)
            else:
                filtered = self.filter(run=run, training_games_enabled=True)
        else:
            if for_rating_games:
                filtered = self.filter(run=run, rating_games_enabled=True)
            else:
                filtered = self.filter(run=run)

        if network_delay is not None:
            max_time = timezone.now() - timedelta(seconds=network_delay)
            filtered = filtered.filter(created_at__lte=max_time)

        return filtered

    def select_most_recent(self, run: Run, for_training_games=False, for_rating_games=False, network_delay=None):
        filtered = self.select_networks_for_run(run, for_training_games=for_training_games, for_rating_games=for_rating_games, network_delay=network_delay)
        return filtered.latest("created_at")

    def select_high_lower_confidence(self, run: Run, for_training_games=False, for_rating_games=False, network_delay=None):
        filtered = self.select_networks_for_run(run, for_training_games=for_training_games, for_rating_games=for_rating_games, network_delay=network_delay)
        return filtered.order_by("-log_gamma_lower_confidence", "?").first()

    def select_high_upper_confidence(self, run: Run, for_training_games=False, for_rating_games=False, network_delay=None):
        filtered = self.select_networks_for_run(run, for_training_games=for_training_games, for_rating_games=for_rating_games, network_delay=network_delay)
        best_networks = filtered.order_by("-log_gamma_upper_confidence", "?")[:10]
        if len(best_networks) <= 0:
            return None
        return random_weighted_choice(best_networks)

    def select_high_uncertainty(self, run: Run, for_training_games=False, for_rating_games=False, network_delay=None):
        filtered = self.select_networks_for_run(run, for_training_games=for_training_games, for_rating_games=for_rating_games, network_delay=network_delay)
        more_uncertain_networks = filtered.order_by("-log_gamma_uncertainty", "?")[:10]
        if len(more_uncertain_networks) <= 0:
            return None
        return random_weighted_choice(more_uncertain_networks)

    def select_low_data(self, run: Run, for_training_games=False, for_rating_games=False, network_delay=None):
        filtered = self.select_networks_for_run(run, for_training_games=for_training_games, for_rating_games=for_rating_games, network_delay=network_delay)
        low_data_networks = filtered.order_by("log_gamma_game_count","?")[:10]
        if len(low_data_networks) <= 0:
            return None
        return random_weighted_choice(low_data_networks)

    # Arbitrary reasonable cap on the uncertainty we will tolerate when trying to report a strongest network
    def select_strongest_confident(self, run: Run, for_training_games=True, for_rating_games=False, max_uncertainty_elo=100):
        filtered = self.select_networks_for_run(run=run, for_training_games=for_training_games, for_rating_games=for_rating_games)
        not_too_uncertain_networks = filtered.filter(log_gamma_uncertainty__lte=(max_uncertainty_elo / (400.0 * math.log10(math.e))))
        return not_too_uncertain_networks.order_by("-log_gamma_lower_confidence").first()
