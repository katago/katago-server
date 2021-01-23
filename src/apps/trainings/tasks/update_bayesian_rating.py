from src import celery_app
from src.apps.games.models import RatingGame
from src.apps.runs.models import Run
from src.apps.trainings.models import Network
from src.apps.trainings.services import BayesianRatingService


@celery_app.task()
def update_bayesian_rating(for_tests=False):
    """
    Periodically update the current_run network rating
    :return:
    """
    current_run = Run.objects.select_current()
    if current_run is None:
        return

    network_ratings = Network.pandas.get_ratings_dataframe(current_run)
    anchor_network = Network.objects.filter(run=current_run).order_by("pk").first()
    if anchor_network is None:
        return

    detailed_tournament_result = RatingGame.pandas.get_detailed_tournament_results_dataframe(
        current_run, for_tests=for_tests
    )

    assert_no_match_with_same_network = (
        detailed_tournament_result["reference_network"] != detailed_tournament_result["opponent_network"]
    )
    detailed_tournament_result = detailed_tournament_result[assert_no_match_with_same_network]

    bayesian_rating_service = BayesianRatingService(
        network_ratings, anchor_network.id, detailed_tournament_result, current_run.virtual_draw_strength
    )
    new_network_ratings = bayesian_rating_service.update_ratings_iteratively(current_run.elo_number_of_iterations)

    Network.pandas.bulk_update_ratings_from_dataframe(new_network_ratings)
