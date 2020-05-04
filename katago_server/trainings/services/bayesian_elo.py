from math import exp, log
import logging

import pandas as pd

from katago_server.trainings.services.pandas_utils import PandasUtilsService

pandas_utils = PandasUtilsService()

logger = logging.getLogger(__name__)


class BayesianRatingService:
    _simplified_tournament_results = None
    _networks_actual_score = None

    def __init__(self, network_ratings: pd.DataFrame, network_anchor_id, detailed_tournament_results: pd.DataFrame):
        self._network_ratings = network_ratings
        self._network_anchor_id = network_anchor_id
        self._detailed_tournament_results = detailed_tournament_results

    def update_ratings_iteratively(self, number_of_iterations):
        logger.debug("---> network_anchor_id (start)")
        logger.debug(self._network_anchor_id)
        logger.debug("---> network_ratings (start)")
        pandas_utils.print_data_frame(self._network_ratings)
        logger.debug("---> detailed_tournament_results (start)")
        pandas_utils.print_data_frame(self._detailed_tournament_results)

        self._update_network_rating_with_bayesian_prior()
        logger.debug("---> detailed_tournament_results (after bayesian)")
        pandas_utils.print_data_frame(self._detailed_tournament_results)

        self._simplify_tournament_into_win_loss_draw()
        logger.debug("---> simplified_tournament_results (after bayesian)")
        pandas_utils.print_data_frame(self._detailed_tournament_results)

        self._sort_inplace_network_ratings_by_uncertainty()
        logger.debug("---> network_ratings (after sort)")
        pandas_utils.print_data_frame(self._network_ratings)

        self._calculate_networks_actual_score()
        logger.info("---> networks_actual_score")
        pandas_utils.print_data_frame(self._networks_actual_score, level=logging.INFO)

        for iteration_index in range(number_of_iterations):
            for network in self._network_ratings.itertuples():
                network_id = network[0]
                network_log_gamma = network.log_gamma
                self._update_specific_network_log_gamma(network_id, network_log_gamma)
            self._reset_anchor_log_gamma()

        for network in self._network_ratings.itertuples():
            network_id = network[0]
            network_log_gamma = network.log_gamma
            self._update_specific_network_log_gamma_uncertainty(network_id, network_log_gamma)
        self._reset_anchor_log_gamma_uncertainty()

        return self._network_ratings

    def _get_games_played_by_specific_network(self, network_id):
        """
        Utility function to get the number of game played by a network

        :param network_id:
        :return:
        """
        tournament_results_only_total = pd.DataFrame()
        tournament_results_only_total["reference_network"] = self._simplified_tournament_results["reference_network"]
        tournament_results_only_total["opponent_network"] = self._simplified_tournament_results["opponent_network"]
        tournament_results_only_total["nb_games"] = self._simplified_tournament_results["nb_games"]

        games_played_by_specific_network_filter = tournament_results_only_total["reference_network"] == network_id
        return tournament_results_only_total[games_played_by_specific_network_filter]

    def _update_network_rating_with_bayesian_prior(self):
        """
         Whenever a NEW player is added to the above, it is necessary to add a Bayesian prior to obtain good results
         and keep the math from blowing up.
         A reasonable prior is to add a single "virtual draw" between the new player and the immediately previous neural net version.
        """
        virtual_draws_src = []
        network_ids = list(self._network_ratings.index)

        for network in self._network_ratings.itertuples():
            network_id = network[0]
            parent_network_id = network.parent_network__pk

            # Everything blows up if for some reason (eg first network, or deleted network)
            # the parent_network_id does not reference an actual network, so let's check that
            if parent_network_id in network_ids:
                draw1 = {"reference_network": network_id, "opponent_network": parent_network_id, "total_bayesian_virtual_draws": 1}
                draw2 = {"reference_network": parent_network_id, "opponent_network": network_id, "total_bayesian_virtual_draws": 1}
                virtual_draws_src.append(draw1)
                virtual_draws_src.append(draw2)

        virtual_draw = pd.DataFrame(virtual_draws_src)

        tournament_results = pd.merge(self._detailed_tournament_results, virtual_draw, how="outer", on=["reference_network", "opponent_network"])
        # panda_utils.print_data_frame(tournament_results)
        tournament_results.fillna(0, inplace=True)
        self._detailed_tournament_results = tournament_results

    def _simplify_tournament_into_win_loss_draw(self):
        """
        For the rest of the algorithm, we do not need the full detail.
        We indeed consider that win as black or as white is similar.
        """
        tournament_results = pd.DataFrame()

        tournament_results["reference_network"] = self._detailed_tournament_results["reference_network"]
        tournament_results["opponent_network"] = self._detailed_tournament_results["opponent_network"]

        # First compute the total number of games, without forgetting bayesian prior draws
        tournament_results["nb_games"] = 0
        tournament_results["nb_games"] += self._detailed_tournament_results["total_games_white"]
        tournament_results["nb_games"] += self._detailed_tournament_results["total_games_black"]
        tournament_results["nb_games"] += self._detailed_tournament_results["total_bayesian_virtual_draws"]

        # Then the wins
        tournament_results["nb_wins"] = 0
        tournament_results["nb_wins"] += self._detailed_tournament_results["total_wins_white"]
        tournament_results["nb_wins"] += self._detailed_tournament_results["total_wins_black"]

        # Then the draws (or no result), without forgetting bayesian prior draws
        tournament_results["nb_draws"] = 0
        tournament_results["nb_draws"] += self._detailed_tournament_results["total_draw_or_no_result"]
        tournament_results["nb_draws"] += self._detailed_tournament_results["total_bayesian_virtual_draws"]

        # Finally, deduce the loss
        tournament_results["nb_loss"] = tournament_results["nb_games"] - tournament_results["nb_wins"] - tournament_results["nb_draws"]

        # And save it for later usage
        self._simplified_tournament_results = tournament_results

    def _sort_inplace_network_ratings_by_uncertainty(self):
        self._network_ratings.sort_values("log_gamma_uncertainty", ascending=False, inplace=True)

    def _calculate_networks_actual_score(self):
        """
        Compute score = the total number of wins of Pi in games that Pi played, counting draws and no-results as half of a win.
        """
        aggregated_tournament_results = self._simplified_tournament_results.groupby(["reference_network"]).sum()

        networks_actual_score = pd.DataFrame(index=aggregated_tournament_results.index)
        networks_actual_score["actual_score"] = 0
        networks_actual_score["actual_score"] += aggregated_tournament_results["nb_wins"]
        networks_actual_score["actual_score"] += 1 / 2 * aggregated_tournament_results["nb_draws"]

        # panda_utils.print_data_frame(networks_actual_score)

        self._networks_actual_score = networks_actual_score

    def _update_specific_network_log_gamma(self, network_id, network_previous_log_gamma):
        logger.debug("---> network_id")
        logger.debug(network_id)

        expected_score = self._calculate_specific_network_expected_score(network_id, network_previous_log_gamma)
        logger.debug("---> expected_score")
        logger.debug(expected_score)

        actual_score = self._networks_actual_score.loc[network_id, "actual_score"]
        logger.debug("---> actual_score")
        logger.debug(actual_score)
        # Set log_gamma(Pi) := log_gamma(Pi) + log(actual_number_of_win(Pi) / expected_number_win(Pi))
        log_gamma_diff = log(actual_score / expected_score)
        logger.debug("---> log_gamma_diff")
        logger.debug(log_gamma_diff)
        self._network_ratings.loc[network_id, "log_gamma"] += log_gamma_diff

    def _calculate_specific_network_expected_score(self, network_id, network_log_gamma):
        """
        For every game Gj that Pi participated in, compute:
            probability_win(Pi,Gj) = 1 / (1 + exp(log_gamma(opponent of Pi in game Gj) - log_gamma(Pi)))
        Then compute:
            expected_score(Pi) = sum_{all games Gj that Pi participated in} ProbWin(Pi,Gj)

        :param network_id: The network specified
        :param network_log_gamma:
        """
        games_played = self._get_games_played_by_specific_network(network_id)
        logger.debug("---> games_played")
        pandas_utils.print_data_frame(games_played)

        games_played_win_probability_src = []
        for game in games_played.itertuples():
            opponent_network = game.opponent_network
            # pandas_utils.print_data_frame(self._network_ratings)
            opponent_network_log_gamma = self._network_ratings.loc[opponent_network, "log_gamma"]
            # logger.debug("opp")
            # logger.debug(opponent_network_log_gamma)
            # logger.debug("ref")
            # logger.debug(network_log_gamma)
            log_gamma_diff = opponent_network_log_gamma - network_log_gamma
            win_probability = 1 / (1 + exp(log_gamma_diff))
            win_probability_dict = {"reference_network": network_id, "opponent_network": opponent_network, "win_probability": win_probability}
            games_played_win_probability_src.append(win_probability_dict)
        games_played_win_probability = pd.DataFrame(games_played_win_probability_src)

        games_played_data = pd.merge(games_played, games_played_win_probability, how="outer", on=["reference_network", "opponent_network"])

        games_played_expected_score = pd.DataFrame()
        games_played_expected_score["expected_score"] = games_played_data["nb_games"] * games_played_data["win_probability"]

        return games_played_expected_score["expected_score"].sum()

    def _reset_anchor_log_gamma(self):
        """
        With all that, anchor player log_gamma will have changed but it is supposed to stay at 0.
        So subtract the anchor player's log_gamma value from every player's log_gamma, including the anchor player's own log_gamma,
        so that the anchor player is back at log_gamma 0.
        """
        self._network_ratings -= self._network_ratings.loc[self._network_anchor_id, "log_gamma"]

    def _update_specific_network_log_gamma_uncertainty(self, network_id, network_log_gamma):
        precision = self._calculate_specific_network_precision(network_id, network_log_gamma)
        self._network_ratings.loc[network_id, "log_gamma_uncertainty"] = 1 / precision

    def _calculate_specific_network_precision(self, network_id, network_log_gamma):
        """
        Compute the second derivative of the log probability with respect to the particular gamma that we are trying to measure uncertainty of.

        :param network_id:
        :param network_log_gamma:
        :return:
        """
        games_played = self._get_games_played_by_specific_network(network_id)

        games_played_precision_src = []
        for game in games_played.itertuples():
            opponent_network = game.opponent_network
            opponent_network_log_gamma = self._network_ratings.loc[opponent_network, "log_gamma"]
            log_gamma_diff = opponent_network_log_gamma - network_log_gamma
            precision = 1 / pow(exp(log_gamma_diff / 2) + exp(-log_gamma_diff / 2), 2)
            precision_dict = {"reference_network": network_id, "opponent_network": opponent_network, "precision": precision}
            games_played_precision_src.append(precision_dict)
        games_played_precision = pd.DataFrame(games_played_precision_src)

        games_played_data = pd.merge(games_played, games_played_precision, how="outer", on=["reference_network", "opponent_network"])

        games_played_cumulative_precision = pd.DataFrame()
        games_played_cumulative_precision["cumulative_precision"] = games_played_data["nb_games"] * games_played_data["precision"]

        return games_played_cumulative_precision["cumulative_precision"].sum()

    def _reset_anchor_log_gamma_uncertainty(self):
        self._network_ratings.loc[self._network_anchor_id, "log_gamma_uncertainty"] = 0
