import logging
import pandas
from django.db.models import Manager
from django_pandas.io import read_frame
from datetime import datetime, timedelta
from django.utils import timezone

from katago_server.games.managers.rating_game_pandas_queryset import RatingGamePandasQuerySet
from katago_server.runs.models import Run

logger = logging.getLogger(__name__)


class RatingGamePandasManager(Manager):
    """
    RatingGamePandasManager generates a tournament result using RatingGamePandasQuerySet
    which is use to update the Elo ratings.

    Every game played is present BOTH ways. If player 1 plays player 2, then this game
    should be included in the stats for reference_network = player 1 and
    opponent_network = player 2, but ALSO it should be included in the stats for
    reference_network = player 2 and opponent_network = player 1.

    Eg:

        +-------------------+------------------+---------------+---------------+-------+
        | reference_network | opponent_network | wins_as_white | wins_as_black | draws |
        +===================+==================+===============+===============+=======+
        | 1566604           | 1266565          | 22            | 17            | 2     |
        +-------------------+------------------+---------------+---------------+-------+
        | 1566604           | 1755666          | 10            | 7             | 20    |
        +-------------------+------------------+---------------+---------------+-------+
        | 1266565           | 1566604          | 2             | 2             | 2     |
        +-------------------+------------------+---------------+---------------+-------+

    """

    def get_queryset(self):
        return RatingGamePandasQuerySet(self.model, using=self._db)

    def get_detailed_tournament_results_dataframe(self, run: Run, for_tests=False):
        # Avoid a race condition where games might be inserted in the middle of us doing these queries
        # by picking a fixed time cutoff slightly in the past and only asking for things older than that
        # During tests though, don't, so that we don't have to sleep in the test.
        if for_tests:
            before_time = timezone.now() + timedelta(seconds=1)
        else:
            before_time = timezone.now() - timedelta(seconds=15)

        queryset = self.get_queryset()

        tournament_results = read_frame(queryset.get_total_games_count_as_white(run,before_time))
        tournament_results = pandas.merge(
            tournament_results,
            read_frame(queryset.get_total_games_count_as_black(run,before_time)),
            how="outer",
            on=["reference_network", "opponent_network"],
        )
        tournament_results = pandas.merge(
            tournament_results,
            read_frame(queryset.get_total_wins_count_as_white(run,before_time)),
            how="outer",
            on=["reference_network", "opponent_network"],
        )
        tournament_results = pandas.merge(
            tournament_results,
            read_frame(queryset.get_total_wins_count_as_black(run,before_time)),
            how="outer",
            on=["reference_network", "opponent_network"],
        )
        tournament_results = pandas.merge(
            tournament_results,
            read_frame(queryset.get_total_draw_or_no_result_as_white(run,before_time)),
            how="outer",
            on=["reference_network", "opponent_network"],
        )
        tournament_results = pandas.merge(
            tournament_results,
            read_frame(queryset.get_total_draw_or_no_result_as_black(run,before_time)),
            how="outer",
            on=["reference_network", "opponent_network"],
        )
        tournament_results.fillna(0, inplace=True)
        return tournament_results
