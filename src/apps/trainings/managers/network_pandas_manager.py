import logging

import numpy as np
from django.db.models import Manager
from django_pandas.io import read_frame

from src.apps.trainings.managers.network_pandas_queryset import NetworkPandasQuerySet

logger = logging.getLogger(__name__)


class NetworkPandasManager(Manager):
    """
    NetworkPandasManager extract the rating using NetworkPandasQueryset.

    Eg:

        +----------+--------------------+-----------+-----------------------+
        | id       | parent_network__pk | log_gamma | log_gamma_uncertainty |
        +==========+====================+===========+=======================+
        | 1566604  | 1566603            | 2.6568    | 0.00235               |
        +----------+--------------------+-----------+-----------------------+
        | 1266565  | 1266564            | 1.6766    | 0.254                 |
        +----------+--------------------+-----------+-----------------------+
    """

    def get_queryset(self):
        return NetworkPandasQuerySet(self.model, using=self._db)

    def get_ratings_dataframe(self, run):
        rating_qs = (
            self.filter(run=run)
            .values(
                "id",
                "parent_network__pk",
                "log_gamma",
                "log_gamma_uncertainty",
                "log_gamma_game_count",
            )
            .all()
        )
        rating = read_frame(rating_qs)
        rating = rating.set_index("id")
        rating = rating.sort_index()

        rating["parent_network__pk"] = rating["parent_network__pk"].fillna(-1)
        rating["log_gamma"] = rating["log_gamma"].fillna(0)
        rating["log_gamma_uncertainty"] = rating["log_gamma_uncertainty"].fillna(0)
        rating["log_gamma_uncertainty"] = rating["log_gamma_uncertainty"].replace([np.inf, -np.inf], 0)
        rating["log_gamma_game_count"] = rating["log_gamma_game_count"].fillna(0)

        return rating

    def bulk_update_ratings_from_dataframe(self, dataframe):
        networks_db = self.all()

        dataframe["log_gamma_upper_confidence"] = dataframe["log_gamma"] + 2 * dataframe["log_gamma_uncertainty"]
        dataframe["log_gamma_lower_confidence"] = dataframe["log_gamma"] - 2 * dataframe["log_gamma_uncertainty"]

        for network_db in networks_db:
            # Avoid races where the networks db changed in the meantime
            if network_db.id in dataframe.index:
                network_db.log_gamma = dataframe.loc[network_db.id, "log_gamma"]
                network_db.log_gamma_uncertainty = dataframe.loc[network_db.id, "log_gamma_uncertainty"]
                network_db.log_gamma_upper_confidence = dataframe.loc[network_db.id, "log_gamma_upper_confidence"]
                network_db.log_gamma_lower_confidence = dataframe.loc[network_db.id, "log_gamma_lower_confidence"]
                network_db.log_gamma_game_count = dataframe.loc[network_db.id, "log_gamma_game_count"]

        self.bulk_update(
            networks_db,
            [
                "log_gamma",
                "log_gamma_uncertainty",
                "log_gamma_upper_confidence",
                "log_gamma_lower_confidence",
                "log_gamma_game_count",
            ],
        )
