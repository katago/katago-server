import pandas
from django.db.models import Manager
from django_pandas.io import read_frame

from katago_server.games.managers.rating_game_pandas_queryset import RatingGamePandasQuerySet
from katago_server.runs.models import Run


class RatingGamePandasManager(Manager):
    """
    RatingGamePandasManager generate a tournament result using RatingGamePandasQuerySet
    which is use to update the rating.

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

    def get_detailed_tournament_results_dataframe(self, run: Run):
        tournament_results = read_frame(self.get_queryset().get_total_games_count_as_white(run))
        tournament_results = pandas.merge(
            tournament_results,
            read_frame(self.get_queryset().get_total_games_count_as_black(run)),
            how="outer",
            on=["reference_network", "opponent_network"],
        )
        tournament_results = pandas.merge(
            tournament_results,
            read_frame(self.get_queryset().get_total_wins_count_as_white(run)),
            how="outer",
            on=["reference_network", "opponent_network"],
        )
        tournament_results = pandas.merge(
            tournament_results,
            read_frame(self.get_queryset().get_total_wins_count_as_black(run)),
            how="outer",
            on=["reference_network", "opponent_network"],
        )
        tournament_results = pandas.merge(
            tournament_results,
            read_frame(self.get_queryset().get_total_draw_or_no_result(run)),
            how="outer",
            on=["reference_network", "opponent_network"],
        )
        tournament_results.fillna(0, inplace=True)
        return tournament_results
