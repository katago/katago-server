from config import celery_app

from katago_server.games.models import RatingGame
from katago_server.runs.models import Run
from katago_server.trainings.models import Network, NetworkBayesianRatingConfiguration
from katago_server.trainings.services.bayesian_elo import BayesianRatingService


@celery_app.task()
def update_bayesian_rating():
    current_run = Run.objects.select_current()

    network_ratings = Network.pd.get_ratings_dataframe(current_run)
    anchor_network = Network.objects.filter(run=current_run).order_by("pk").first()
    detailed_tournament_result = RatingGame.pd.get_detailed_tournament_results_dataframe(current_run)

    assert_no_match_with_same_network = detailed_tournament_result["reference_network"] != detailed_tournament_result["opponent_network"]
    detailed_tournament_result = detailed_tournament_result[assert_no_match_with_same_network]

    nb_of_iterations = NetworkBayesianRatingConfiguration.get_solo().number_of_iterations

    bayesian_rating_service = BayesianRatingService(network_ratings, anchor_network.id, detailed_tournament_result)
    new_network_ratings = bayesian_rating_service.update_ratings_iteratively(nb_of_iterations)

    Network.pd.bulk_update_ratings_from_dataframe(new_network_ratings)
