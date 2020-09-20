from django.db.models import QuerySet, Count, Q, F
from django.apps import apps

from datetime import datetime, timedelta

from src.apps.runs.models import Run


class RatingGamePandasQuerySet(QuerySet):
    """
    RatingGamePandasQuerySet query the db and return the number of times network faces with another network, wins as black or as white,
    or draws
    """

    def get_total_games_count_as_white(self, run: Run, before_time):
        total_games_count_aggregate = Count("id")
        return (
            self.filter(run=run,created_at__lt=before_time)
            .values(reference_network=F("white_network__pk"), opponent_network=F("black_network__pk"),)
            .order_by()
            .annotate(total_games_white=total_games_count_aggregate)
        )

    def get_total_games_count_as_black(self, run: Run, before_time):
        total_games_count_aggregate = Count("id")
        return (
            self.filter(run=run,created_at__lt=before_time)
            .values(reference_network=F("black_network__pk"), opponent_network=F("white_network__pk"),)
            .order_by()
            .annotate(total_games_black=total_games_count_aggregate)
        )

    def get_total_wins_count_as_white(self, run: Run, before_time):
        RatingGame = apps.get_model("games.RatingGame")
        is_white_win = Q(winner=RatingGame.GamesResult.WHITE)
        total_wins_as_white_count_aggregate = Count("id", filter=is_white_win)
        return (
            self.filter(run=run,created_at__lt=before_time)
            .values(reference_network=F("white_network__pk"), opponent_network=F("black_network__pk"),)
            .order_by()
            .annotate(total_wins_white=total_wins_as_white_count_aggregate)
        )

    def get_total_wins_count_as_black(self, run: Run, before_time):
        RatingGame = apps.get_model("games.RatingGame")
        is_black_win = Q(winner=RatingGame.GamesResult.BLACK)
        total_wins_as_black_count_aggregate = Count("id", filter=is_black_win)
        return (
            self.filter(run=run,created_at__lt=before_time)
            .values(reference_network=F("black_network__pk"), opponent_network=F("white_network__pk"),)
            .order_by()
            .annotate(total_wins_black=total_wins_as_black_count_aggregate)
        )

    def get_total_draw_or_no_result_as_white(self, run: Run, before_time):
        RatingGame = apps.get_model("games.RatingGame")
        is_draw_or_no_result = Q(winner=RatingGame.GamesResult.DRAW) | Q(winner=RatingGame.GamesResult.NO_RESULT)
        total_draw_or_no_result_count_aggregate = Count("id", filter=is_draw_or_no_result)
        return (
            self.filter(run=run,created_at__lt=before_time)
            .values(reference_network=F("white_network__pk"), opponent_network=F("black_network__pk"),)
            .order_by()
            .annotate(total_draw_or_no_result_white=total_draw_or_no_result_count_aggregate)
        )

    def get_total_draw_or_no_result_as_black(self, run: Run, before_time):
        RatingGame = apps.get_model("games.RatingGame")
        is_draw_or_no_result = Q(winner=RatingGame.GamesResult.DRAW) | Q(winner=RatingGame.GamesResult.NO_RESULT)
        total_draw_or_no_result_count_aggregate = Count("id", filter=is_draw_or_no_result)
        return (
            self.filter(run=run,created_at__lt=before_time)
            .values(reference_network=F("black_network__pk"), opponent_network=F("white_network__pk"),)
            .order_by()
            .annotate(total_draw_or_no_result_black=total_draw_or_no_result_count_aggregate)
        )
