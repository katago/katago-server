import logging
from math import exp, log

from celery.signals import worker_ready
from django.db.models import Q

from config import celery_app
from katago_server.games.models import RankingEstimationGame
from katago_server.trainings.models import Network

logger = logging.getLogger(__name__)

ITERATION_NB = 10


@worker_ready.connect
def on_worker_ready(sender=None, conf=None, **kwargs):
    logger.info("Server started")
    update_bayesian_ranking.delay()


@celery_app.task
def update_bayesian_ranking():
    # Take all network except the first one
    # The first network is the "anchor" network
    # we use the slice syntax on queryset: https://stackoverflow.com/a/40758944
    anchor_network = Network.objects.order_by("created_at")[1]
    # updating the bayesian ranking is iterative
    all_network_sorted_by_uncertainty = Network.objects.order_by("-log_gamma_uncertainty")
    for iteration_index in range(ITERATION_NB):
        for network in all_network_sorted_by_uncertainty:
            # (ALGORITHM): 1. Compute actual_number_of_win = the total number of wins of Pi in games that Pi played, counting draws and no-results as half of a win.
            actual_number_of_win = 0
            r = RankingEstimationGame.GamesResult.DRAW
            # Add 1 for each win
            match_won_filter = (Q(black_network=network) & Q(result=r.BLACK)) | (Q(white_network=network) | Q(result=r.WHITE))
            actual_number_of_win += RankingEstimationGame.objects.count().filter(match_won_filter)
            # And 1/2 for draw or no match
            match_with_no_victory_filter = (Q(black_network=network) | Q(white_network=network)) & (Q(result=r.DRAW) | Q(result=r.MOSHOUBOU))
            actual_number_of_win += 1/2 * RankingEstimationGame.objects.count().filter(match_with_no_victory_filter)
            # (ALGORITHM): 2. For every game Gj that Pi participated in, compute probability_win(Pi,Gj) = 1 / (1 + exp(log_gamma(opponent of Pi in game Gj) - log_gamma(Pi)))
            # (ALGORITHM): 3. Compute expected_number_win(Pi) = sum_{all games Gj that Pi participated in} ProbWin(Pi,Gj)
            expected_number_win = 0
            current_log_gamma = network.log_gamma
            all_games_played = RankingEstimationGame.objects.filter(Q(black_network=network) | Q(white_network=network)).prefetch_related("black_network", "white_network")
            for game in all_games_played:
                probability_win = 0
                if network == game.black_network:
                    probability_win = 1 / (1 + exp(game.white_network.log_gamma - current_log_gamma))
                if network == game.white_network:
                    probability_win = 1 / (1 + exp(game.black_network.log_gamma - current_log_gamma))
                expected_number_win += probability_win
            # (ALGORITHM): 4. Set log_gamma(Pi) := log_gamma(Pi) + log(actual_number_of_win(Pi) / expected_number_win(Pi))
            network.log_gamma = network.log_gamma + log(actual_number_of_win / expected_number_win)
            network.save()
        # (ALGORITHM): 5. so subtract the anchor player's log_gamma value from every player's log_gamma, including the anchor player's own log_gamma, so that the anchor player is back at log_gamma 0.
        anchor_log_gamma = anchor_network.log_gamma
        if anchor_log_gamma != 0:
            for network in all_network_sorted_by_uncertainty:
                network.log_gamma = network.log_gamma - anchor_log_gamma
                network.save()
    # (ALGORITHM): 6. the LogGammaUncertainty values can be recomputed once at the end as follows:
    for network in all_network_sorted_by_uncertainty:
        all_games_played = RankingEstimationGame.objects.filter(Q(black_network=network) | Q(white_network=network)).prefetch_related("black_network", "white_network")
        total_precision = 0
        current_log_gamma = network.log_gamma
        for game in all_games_played:
            log_gamma_difference = 0
            if network == game.black_network:
                log_gamma_difference = game.white_network.log_gamma - current_log_gamma
            if network == game.white_network:
                log_gamma_difference = game.black_network.log_gamma - current_log_gamma
            game_precision = 1 / pow(exp(log_gamma_difference / 2) + exp(-log_gamma_difference / 2), 2)
            total_precision += game_precision
        network.log_gamma_uncertainty = 1 / total_precision
        network.save()
