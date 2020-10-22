from django.db.models import CharField, DateTimeField, IntegerField, ForeignKey, OneToOneField, DO_NOTHING

from django_pgviews import view as pg

from src.apps.trainings.models import Network
from src.apps.runs.models import Run


class GameCountByNetwork(pg.MaterializedView):
    """
    A materialized view that serves extremely fast access to slightly-outdated counts of rating and games by network
    """

    concurrent_index = "network_id"

    sql = """
    SELECT
      trainingcounts.*,
      ratingcounts.total_num_rating_games as total_num_rating_games,
      ratingcounts.total_rating_score as total_rating_score,
      trainings_network.name as network_name,
      trainings_network.run_id as run_id,
      trainings_network.created_at as network_created_at
    FROM (
      SELECT
      black_network_id as network_id,
      count(*) as total_num_training_games,
      sum(num_training_rows) as total_num_training_rows
      FROM games_traininggame
      GROUP BY black_network_id
    ) trainingcounts
    INNER JOIN
    (
      SELECT network_id, sum(num_games) as total_num_rating_games, sum(score) as total_rating_score
      FROM
      (
        (
          SELECT
          black_network_id as network_id,
          count(*) as num_games,
          sum(case when winner = 'B' then 1 when winner = 'W' then 0 else 0.5 end) as score
          FROM games_ratinggame
          GROUP BY black_network_id
        )
        UNION ALL
        (
          SELECT
          white_network_id as network_id,
          count(*) as num_games,
          sum(case when winner = 'W' then 1 when winner = 'B' then 0 else 0.5 end) as score
          FROM games_ratinggame
          GROUP BY white_network_id
        )
      ) subquery
      GROUP BY network_id
    ) ratingcounts
    ON trainingcounts.network_id = ratingcounts.network_id
    INNER JOIN
    trainings_network
    ON trainingcounts.network_id = trainings_network.id
    """

    network = OneToOneField(Network, primary_key=True, db_index=True, db_constraint=False, on_delete=DO_NOTHING)
    run = ForeignKey(Run, db_index=True, db_constraint=False, on_delete=DO_NOTHING)
    network_name = CharField(max_length=128, db_index=True)
    network_created_at = DateTimeField(db_index=True)

    total_num_training_games = IntegerField(null=False, db_index=True)
    total_num_training_rows = IntegerField(null=False)
    total_num_rating_games = IntegerField(null=False, db_index=True)
    total_rating_score = IntegerField(null=False)

    class Meta:
        managed = False
        db_table = "games_gamecountbynetwork"

