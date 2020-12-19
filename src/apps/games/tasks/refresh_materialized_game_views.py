from src import celery_app

from src.apps.games.models import GameCountByNetwork, GameCountByUser, RecentGameCountByUser, DayGameCountByUser


@celery_app.task()
def refresh_materialized_game_views():
    """
    Refresh all the materialized views for games app
    :return:
    """
    GameCountByNetwork.refresh(concurrently=True)
    GameCountByUser.refresh(concurrently=True)
    RecentGameCountByUser.refresh(concurrently=True)
    DayGameCountByUser.refresh(concurrently=True)
