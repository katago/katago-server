from django.db.models import DO_NOTHING, CharField, DateTimeField, ForeignKey, IntegerField, OneToOneField
from django_pgviews import view as pg

from src.apps.runs.models import Run
from src.apps.trainings.models import Network
from src.apps.users.models import User

__ALL__ = ["GameCountByNetwork", "GameCountByUser", "RecentGameCountByUser", "DayGameCountByUser"]


class GameCountByNetwork(pg.MaterializedView):
    """
    A materialized view that serves extremely fast access to slightly-outdated counts of rating and games by network
    """

    concurrent_index = "network_id"

    sql = """
    SELECT
      counts.*,
      trainings_network.name as network_name,
      trainings_network.run_id as run_id,
      trainings_network.created_at as network_created_at
    FROM
    (
      SELECT
        COALESCE(trainingcounts.network_id, ratingcounts.network_id) as network_id,
        COALESCE(trainingcounts.total_num_training_games, 0) as total_num_training_games,
        COALESCE(trainingcounts.total_num_training_rows, 0) as total_num_training_rows,
        COALESCE(ratingcounts.total_num_rating_games, 0) as total_num_rating_games,
        COALESCE(ratingcounts.total_rating_score,0.0) as total_rating_score
      FROM (
        SELECT
        black_network_id as network_id,
        count(*) as total_num_training_games,
        sum(num_training_rows) as total_num_training_rows
        FROM games_traininggame
        GROUP BY black_network_id
      ) trainingcounts
      FULL OUTER JOIN
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
    ) counts
    INNER JOIN
    trainings_network
    ON counts.network_id = trainings_network.id
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


class GameCountByUser(pg.MaterializedView):
    """
    A materialized view that serves extremely fast access to slightly-outdated counts of rating and games by user
    """

    concurrent_index = "id"

    sql = """
    SELECT
      counts.*,
      CONCAT(counts.run_id, '|', counts.user_id) as id,
      users_user.username as username
    FROM (
      SELECT
        COALESCE(trainingcounts.submitted_by_id, ratingcounts.submitted_by_id) as user_id,
        COALESCE(trainingcounts.run_id, ratingcounts.run_id) as run_id,
        COALESCE(trainingcounts.total_num_training_games, 0) as total_num_training_games,
        COALESCE(trainingcounts.total_num_training_rows, 0) as total_num_training_rows,
        COALESCE(ratingcounts.total_num_rating_games, 0) as total_num_rating_games
      FROM (
        SELECT
        submitted_by_id,
        run_id,
        count(*) as total_num_training_games,
        sum(num_training_rows) as total_num_training_rows
        FROM games_traininggame
        GROUP BY submitted_by_id, run_id
      ) trainingcounts
      FULL OUTER JOIN
      (
        SELECT
        submitted_by_id,
        run_id,
        count(*) as total_num_rating_games
        FROM games_ratinggame
        GROUP BY submitted_by_id, run_id
      ) ratingcounts
      ON trainingcounts.submitted_by_id = ratingcounts.submitted_by_id
      AND trainingcounts.run_id = ratingcounts.run_id
    ) counts
    INNER JOIN
    users_user
    ON counts.user_id = users_user.id
    """

    # Django insists on having a single primary key field. So we smash user and run together
    # to make this single field to make django happy
    id = CharField(max_length=128, primary_key=True, db_index=True)

    user = ForeignKey(User, db_index=True, db_constraint=False, on_delete=DO_NOTHING)
    run = ForeignKey(Run, db_index=True, db_constraint=False, on_delete=DO_NOTHING)
    username = CharField(max_length=255, db_index=True)

    total_num_training_games = IntegerField(null=False, db_index=True)
    total_num_training_rows = IntegerField(null=False)
    total_num_rating_games = IntegerField(null=False, db_index=True)

    class Meta:
        managed = False
        db_table = "games_gamecountbyuser"


class TimeSpanGameCountByUser(pg.MaterializedView):
    """
    A materialized view that serves extremely fast access to slightly-outdated counts of rating and games by user
    in the last certain amount of time.
    """

    concurrent_index = "id"

    @staticmethod
    def make_sql(sql_interval_str):
        return """
    SELECT
      counts.*,
      CONCAT(counts.run_id, '|', counts.user_id) as id,
      users_user.username as username
    FROM (
      SELECT
        COALESCE(trainingcounts.submitted_by_id, ratingcounts.submitted_by_id) as user_id,
        COALESCE(trainingcounts.run_id, ratingcounts.run_id) as run_id,
        COALESCE(trainingcounts.total_num_training_games, 0) as total_num_training_games,
        COALESCE(trainingcounts.total_num_training_rows, 0) as total_num_training_rows,
        COALESCE(ratingcounts.total_num_rating_games, 0) as total_num_rating_games
      FROM (
        SELECT
        submitted_by_id,
        run_id,
        count(*) as total_num_training_games,
        sum(num_training_rows) as total_num_training_rows
        FROM games_traininggame
        WHERE created_at >= NOW() - INTERVAL '%s'
        GROUP BY submitted_by_id, run_id
      ) trainingcounts
      FULL OUTER JOIN
      (
        SELECT
        submitted_by_id,
        run_id,
        count(*) as total_num_rating_games
        FROM games_ratinggame
        WHERE created_at >= NOW() - INTERVAL '%s'
        GROUP BY submitted_by_id, run_id
      ) ratingcounts
      ON trainingcounts.submitted_by_id = ratingcounts.submitted_by_id
      AND trainingcounts.run_id = ratingcounts.run_id
    ) counts
    INNER JOIN
    users_user
    ON counts.user_id = users_user.id
    """ % (
            sql_interval_str,
            sql_interval_str,
        )

    # Django insists on having a single primary key field. So we smash user and run together
    # to make this single field to make django happy
    id = CharField(max_length=128, primary_key=True, db_index=True)

    user = ForeignKey(User, db_index=True, db_constraint=False, on_delete=DO_NOTHING)
    run = ForeignKey(Run, db_index=True, db_constraint=False, on_delete=DO_NOTHING)
    username = CharField(max_length=255, db_index=True)

    total_num_training_games = IntegerField(null=False, db_index=True)
    total_num_training_rows = IntegerField(null=False)
    total_num_rating_games = IntegerField(null=False, db_index=True)

    class Meta:
        abstract = True


class RecentGameCountByUser(TimeSpanGameCountByUser):
    sql = TimeSpanGameCountByUser.make_sql("1 week")

    class Meta:
        managed = False
        db_table = "games_recentgamecountbyuser"


class DayGameCountByUser(TimeSpanGameCountByUser):
    sql = TimeSpanGameCountByUser.make_sql("1 day")

    class Meta:
        managed = False
        db_table = "games_daygamecountbyuser"
