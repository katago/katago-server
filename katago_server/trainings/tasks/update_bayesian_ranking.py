from config import celery_app

from katago_server.games.models import RatingGame
from katago_server.runs.models import Run
from katago_server.trainings.models import Network, NetworkBayesianRankingConfiguration
from katago_server.trainings.services.bayesian_elo import BayesianRankingService


@celery_app.task()
def update_bayesian_ranking():
    current_run = Run.objects.select_current()

    network_rankings = Network.pd.get_rankings_dataframe(current_run)
    anchor_network = Network.objects.filter(run=current_run).order_by("pk").first()
    detailed_tournament_result = RatingGame.pd.get_detailed_tournament_results_dataframe(current_run)

    assert_no_match_with_same_network = detailed_tournament_result["reference_network"] != detailed_tournament_result["opponent_network"]
    detailed_tournament_result = detailed_tournament_result[assert_no_match_with_same_network]

    nb_of_iterations = NetworkBayesianRankingConfiguration.get_solo().number_of_iterations

    bayesian_ranking_service = BayesianRankingService(network_rankings, anchor_network.id, detailed_tournament_result)
    new_network_rankings = bayesian_ranking_service.update_rankings_iteratively(nb_of_iterations)

    Network.pd.bulk_update_rankings_from_dataframe(new_network_rankings)
