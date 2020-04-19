from django.db.models import QuerySet, Count, Q, F
from django.apps import apps

from katago_server.runs.models import Run


class RankingEstimationGamePdQuerySet(QuerySet):
    def get_total_games_count_as_white(self, run: Run):
        total_games_count_aggregate = Count("id")
        return self.filter(run=run).values(reference_network=F("white_network__pk"), opponent_network=F("black_network__pk")).annotate(
            total_games_white=total_games_count_aggregate
        )

    def get_total_games_count_as_black(self, run: Run):
        total_games_count_aggregate = Count("id")
        return self.filter(run=run).values(reference_network=F("black_network__pk"), opponent_network=F("white_network__pk")).annotate(
            total_games_black=total_games_count_aggregate
        )

    def get_total_wins_count_as_white(self, run: Run):
        RankingEstimationGame = apps.get_model("games.RankingEstimationGame")
        is_white_win = Q(result=RankingEstimationGame.GamesResult.WHITE)
        total_wins_as_white_count_aggregate = Count("id", filter=is_white_win)
        return self.filter(run=run).values(reference_network=F("white_network__pk"), opponent_network=F("black_network__pk")).annotate(
            total_wins_white=total_wins_as_white_count_aggregate
        )

    def get_total_wins_count_as_black(self, run: Run):
        RankingEstimationGame = apps.get_model("games.RankingEstimationGame")
        is_black_win = Q(result=RankingEstimationGame.GamesResult.BLACK)
        total_wins_as_black_count_aggregate = Count("id", filter=is_black_win)
        return self.filter(run=run).values(reference_network=F("black_network__pk"), opponent_network=F("white_network__pk")).annotate(
            total_wins_black=total_wins_as_black_count_aggregate
        )

    def get_total_draw_or_no_result(self, run: Run):
        RankingEstimationGame = apps.get_model("games.RankingEstimationGame")
        is_draw_or_no_result = Q(result=RankingEstimationGame.GamesResult.DRAW) | Q(result=RankingEstimationGame.GamesResult.NO_RESULT)
        total_draw_or_no_result_count_aggregate = Count("id", filter=is_draw_or_no_result)
        return self.filter(run=run).values(reference_network=F("white_network__pk"), opponent_network=F("black_network__pk")).annotate(
            total_draw_or_no_result=total_draw_or_no_result_count_aggregate
        )
