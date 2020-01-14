import logging
from math import exp, log, log10, e

import numpy
import pandas

from django.db.models import Q, Count
from django_pandas.io import read_frame

from config import celery_app
from katago_server.games.models import RankingEstimationGame
from katago_server.trainings.models import Network, RankingGameGeneratorConfiguration

logger = logging.getLogger(__name__)


def _print_full_data_frame(x):
    pandas.set_option('display.max_rows', len(x))
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 2000)
    pandas.set_option('display.float_format', '{:20,.3f}'.format)
    pandas.set_option('display.max_colwidth', -1)
    logger.info('-----> \n' + x.to_string())
    pandas.reset_option('display.max_rows')
    pandas.reset_option('display.max_columns')
    pandas.reset_option('display.width')
    pandas.reset_option('display.float_format')
    pandas.reset_option('display.max_colwidth')


def _get_all_networks_data_frame():
    all_networks_qs = Network.objects.all()
    all_networks = read_frame(all_networks_qs, fieldnames=["id", "parent_network__pk", "log_gamma", "log_gamma_uncertainty"])

    all_networks = all_networks.set_index("id")
    all_networks = all_networks.sort_index()
    all_networks = all_networks.fillna(-1)

    return all_networks


def _get_detailed_tournament_result_data_frame():
    total_games_aggregate = Count('id')
    win_white_aggregate = Count('id', filter=Q(result=RankingEstimationGame.GamesResult.WHITE))
    win_black_aggregate = Count('id', filter=Q(result=RankingEstimationGame.GamesResult.BLACK))
    draw_aggregate = Count('id', filter=Q(result=RankingEstimationGame.GamesResult.DRAW) | Q(result=RankingEstimationGame.GamesResult.NO_RESULT))

    network_tournament_result_total_games_white_qs = RankingEstimationGame.objects.values('white_network__pk', 'black_network__pk').annotate(total_games_white=total_games_aggregate)
    network_tournament_result_total_games_white = read_frame(network_tournament_result_total_games_white_qs, fieldnames=['white_network__pk', 'black_network__pk', 'total_games_white'])
    network_tournament_result_total_games_white = network_tournament_result_total_games_white.rename(columns={'white_network__pk': 'reference_network', 'black_network__pk': 'opponent_network'}, errors="raise")

    network_tournament_result_total_games_black_qs = RankingEstimationGame.objects.values('black_network__pk', 'white_network__pk').annotate(total_games_black=total_games_aggregate)
    network_tournament_result_total_games_black = read_frame(network_tournament_result_total_games_black_qs, fieldnames=['white_network__pk', 'black_network__pk', 'total_games_black'])
    network_tournament_result_total_games_black = network_tournament_result_total_games_black.rename(columns={'black_network__pk': 'reference_network', 'white_network__pk': 'opponent_network'}, errors="raise")

    network_tournament_result_white_win_qs = RankingEstimationGame.objects.values('white_network__pk', 'black_network__pk').annotate(win_count_white=win_white_aggregate)
    network_tournament_result_white_win = read_frame(network_tournament_result_white_win_qs, fieldnames=['white_network__pk', 'black_network__pk', 'win_count_white'])
    network_tournament_result_white_win = network_tournament_result_white_win.rename(columns={'white_network__pk': 'reference_network', 'black_network__pk': 'opponent_network'}, errors="raise")

    network_tournament_result_black_win_qs = RankingEstimationGame.objects.values('black_network__pk', 'white_network__pk').annotate(win_count_black=win_black_aggregate)
    network_tournament_result_black_win = read_frame(network_tournament_result_black_win_qs, fieldnames=['white_network__pk', 'black_network__pk', 'win_count_black'])
    network_tournament_result_black_win = network_tournament_result_black_win.rename(columns={'black_network__pk': 'reference_network', 'white_network__pk': 'opponent_network'}, errors="raise")

    network_tournament_result_draw_qs = RankingEstimationGame.objects.values('white_network__pk', 'black_network__pk').annotate(draw_count=draw_aggregate)
    network_tournament_result_draw = read_frame(network_tournament_result_draw_qs, fieldnames=['white_network__pk', 'black_network__pk', 'draw_count'])
    network_tournament_result_draw = network_tournament_result_draw.rename(columns={'white_network__pk': 'reference_network', 'black_network__pk': 'opponent_network'}, errors="raise")

    network_tournament_result = pandas.merge(network_tournament_result_total_games_white, network_tournament_result_total_games_black, how='outer', on=['reference_network', 'opponent_network'])
    network_tournament_result = pandas.merge(network_tournament_result, network_tournament_result_white_win, how='outer', on=['reference_network', 'opponent_network'])
    network_tournament_result = pandas.merge(network_tournament_result, network_tournament_result_black_win, how='outer', on=['reference_network', 'opponent_network'])
    network_tournament_result = pandas.merge(network_tournament_result, network_tournament_result_draw, how='outer', on=['reference_network', 'opponent_network'])

    network_tournament_result = network_tournament_result.fillna(0)

    return network_tournament_result


def _add_bayesian_prior(all_networks: pandas.DataFrame, tournament_result: pandas.DataFrame):
    """
    Whenever a NEW player is added to the above, it is necessary to add a Bayesian prior to obtain good results and keep the math from blowing up.
    A reasonable prior is to add a single "virtual draw" between the new player and the immediately previous neural net version

    :param all_networks:
    :param tournament_result:
    :return:
    """
    virtual_draw_dict = []
    for index, network in all_networks.iterrows():
        if network.parent_network__pk > 0:
            draw1 = {
                "reference_network": index,
                "opponent_network": network.parent_network__pk,
                "virtual_draw_count": 1
            }
            draw2 = {
                "reference_network": network.parent_network__pk,
                "opponent_network": index,
                "virtual_draw_count": 1
            }
            virtual_draw_dict.append(draw1)
            virtual_draw_dict.append(draw2)
    virtual_draw = pandas.DataFrame(virtual_draw_dict)

    tournament_result = pandas.merge(tournament_result, virtual_draw, how='outer', on=['reference_network', 'opponent_network'])
    tournament_result = tournament_result.fillna(0)

    return tournament_result


def _simplify_network_tournament_result(detailed_tournament_result: pandas.DataFrame):
    tournament_result = pandas.DataFrame()

    tournament_result['reference_network'] = detailed_tournament_result['reference_network']
    tournament_result['opponent_network'] = detailed_tournament_result['opponent_network']

    tournament_result['total'] = detailed_tournament_result['total_games_white'] + detailed_tournament_result['total_games_black'] + detailed_tournament_result['virtual_draw_count']
    tournament_result['win'] = detailed_tournament_result['win_count_white'] + detailed_tournament_result['win_count_black']
    tournament_result['draw'] = detailed_tournament_result['draw_count'] + detailed_tournament_result['virtual_draw_count']
    tournament_result['loss'] = tournament_result['total'] - tournament_result['win'] - tournament_result['draw']

    return tournament_result


def _calculate_all_networks_actual_wins(tournament_result: pandas.DataFrame):
    """
    Compute actual_number_of_win = the total number of wins of Pi in games that Pi played, counting draws and no-results as half of a win.

    :param tournament_result:
    :return:
    """
    tournament_result = tournament_result.drop(columns=["opponent_network", "total"])

    all_networks_actual_wins = tournament_result.groupby(["reference_network"]).sum()
    all_networks_actual_wins['actual_wins'] = all_networks_actual_wins['win'] + 1 / 2 * all_networks_actual_wins['draw']
    all_networks_actual_wins = all_networks_actual_wins.drop(columns=["win", "draw", "loss"])

    return all_networks_actual_wins


def _calculate_one_network_expected_wins(reference_network, all_networks: pandas.DataFrame, tournament_nb_games: pandas.DataFrame):
    """
    For every game Gj that Pi participated in, compute probability_win(Pi,Gj) = 1 / (1 + exp(log_gamma(opponent of Pi in game Gj) - log_gamma(Pi)))
    Then Compute expected_number_win(Pi) = sum_{all games Gj that Pi participated in} ProbWin(Pi,Gj)

    :param reference_network:
    :param all_networks:
    :param tournament_nb_games:
    :return:
    """
    games_played = tournament_nb_games[tournament_nb_games.reference_network == reference_network[0]]
    reference_network_log_gamma = reference_network.log_gamma

    tournament_fight_probabilities = []
    for game in games_played.itertuples():
        opponent_network = game.opponent_network
        opponent_network_log_gamma = all_networks.loc[opponent_network, 'log_gamma']
        probability_win = 1 / (1 + exp(opponent_network_log_gamma - reference_network_log_gamma))
        tournament_fight_probabilities.append({"reference_network": reference_network[0], "opponent_network": opponent_network, "probability_win": probability_win})

    games_played_probabilities = pandas.DataFrame(tournament_fight_probabilities)
    games_played_expected = pandas.merge(games_played, games_played_probabilities, how='outer', on=['reference_network', 'opponent_network'])
    games_played_expected['expected_wins'] = games_played_expected['total'] * games_played_expected['probability_win']
    games_played_expected = games_played_expected.drop(columns=["opponent_network", "total", "probability_win"])

    return games_played_expected.groupby(["reference_network"]).sum().loc[reference_network[0], 'expected_wins']


def _calculate_one_network_precision(reference_network, all_networks: pandas.DataFrame, tournament_nb_games: pandas.DataFrame):
    games_played = tournament_nb_games[tournament_nb_games.reference_network == reference_network[0]]
    reference_network_log_gamma = reference_network.log_gamma

    tournament_fight_precision = []
    for game in games_played.itertuples():
        opponent_network = game.opponent_network
        opponent_network_log_gamma = all_networks.loc[opponent_network, 'log_gamma']
        log_gamma_difference = opponent_network_log_gamma - reference_network_log_gamma
        precision = 1 / pow(exp(log_gamma_difference / 2) + exp(- log_gamma_difference / 2), 2)
        tournament_fight_precision.append({"reference_network": reference_network[0], "opponent_network": opponent_network, "precision": precision})

    games_played_precision = pandas.DataFrame(tournament_fight_precision)
    games_played_cumulative_precision = pandas.merge(games_played, games_played_precision, how='outer', on=['reference_network', 'opponent_network'])
    games_played_cumulative_precision['cumulative_precision'] = games_played_cumulative_precision['total'] * games_played_cumulative_precision['precision']
    games_played_expected = games_played_cumulative_precision.drop(columns=["opponent_network", "total", "precision"])

    return games_played_expected.groupby(["reference_network"]).sum().loc[reference_network[0], 'cumulative_precision']


def _bulk_update_networks(all_networks: pandas.DataFrame):
    networks_db = Network.objects.all()

    for network_db in networks_db:
        network_db.log_gamma = all_networks.loc[network_db.id, 'log_gamma']
        network_db.log_gamma_uncertainty = all_networks.loc[network_db.id, 'log_gamma_uncertainty']
        network_db.log_gamma_upper_confidence = all_networks.loc[network_db.id, 'log_gamma_upper_confidence']
        network_db.log_gamma_lower_confidence = all_networks.loc[network_db.id, 'log_gamma_lower_confidence']

    Network.objects.bulk_update(networks_db, ['log_gamma', 'log_gamma_uncertainty', 'log_gamma_upper_confidence', 'log_gamma_lower_confidence'])


@celery_app.task()
def update_bayesian_ranking():
    all_networks = _get_all_networks_data_frame()
    anchor_network_id = all_networks.head().index[0]

    tournament_result = _get_detailed_tournament_result_data_frame()
    tournament_result = _add_bayesian_prior(all_networks, tournament_result)
    tournament_result = _simplify_network_tournament_result(tournament_result)

    all_networks = all_networks.drop(columns=["parent_network__pk"]).sort_values("log_gamma_uncertainty", ascending=False)

    all_networks_actual_wins = _calculate_all_networks_actual_wins(tournament_result)
    tournament_nb_games = tournament_result.drop(columns=["win", "draw", "loss"])

    for iteration_index in range(RankingGameGeneratorConfiguration.get_solo().number_of_iterations):
        for network in all_networks.itertuples():
            network_id = network[0]
            network_expected_wins = _calculate_one_network_expected_wins(network, all_networks, tournament_nb_games)
            network_actual_wins = all_networks_actual_wins.loc[network_id, 'actual_wins']
            # Set log_gamma(Pi) := log_gamma(Pi) + log(actual_number_of_win(Pi) / expected_number_win(Pi))
            all_networks.loc[network_id, 'log_gamma'] = all_networks.loc[network_id, 'log_gamma'] + log(network_actual_wins / network_expected_wins)
        # so subtract the anchor player's log_gamma value from every player's log_gamma, including the anchor player's own log_gamma, so that the anchor player is back at log_gamma 0.
        all_networks['log_gamma'] = all_networks['log_gamma'] - all_networks.loc[anchor_network_id, 'log_gamma']

    #  the LogGammaUncertainty values can be recomputed once at the end as follows:
    for network in all_networks.itertuples():
        network_id = network[0]
        network_precision = _calculate_one_network_precision(network, all_networks, tournament_nb_games)
        all_networks.loc[network_id, 'log_gamma_uncertainty'] = 1 / network_precision
    all_networks.loc[anchor_network_id, 'log_gamma_uncertainty'] = 0.

    # perform the update in DB
    all_networks['log_gamma_upper_confidence'] = numpy.round((all_networks['log_gamma'] + 2 * all_networks['log_gamma_uncertainty']) * 400 * log10(e), decimals=2)
    all_networks['log_gamma_lower_confidence'] = numpy.round((all_networks['log_gamma'] - 2 * all_networks['log_gamma_uncertainty']) * 400 * log10(e), decimals=2)
    _bulk_update_networks(all_networks)
