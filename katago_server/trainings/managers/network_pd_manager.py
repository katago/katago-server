from math import log10, e

import numpy as np
from django.db.models import Manager, F
from django_pandas.io import read_frame

from katago_server.trainings.managers.network_pd_queryset import NetworkPdQuerySet


class NetworkPdManager(Manager):
    def get_queryset(self):
        return NetworkPdQuerySet(self.model, using=self._db)

    def get_rankings_dataframe(self):
        ranking_qs = self.values("id", "parent_network__pk", "log_gamma", "log_gamma_uncertainty").all()
        ranking = read_frame(ranking_qs)
        ranking = ranking.set_index("id")
        ranking = ranking.sort_index()

        ranking["parent_network__pk"] = ranking["parent_network__pk"].fillna(-1)
        ranking["log_gamma"] = ranking["log_gamma"].fillna(0)
        ranking["log_gamma_uncertainty"] = ranking["log_gamma_uncertainty"].fillna(0)
        ranking["log_gamma_uncertainty"] = ranking["log_gamma_uncertainty"].replace([np.inf, -np.inf], 0)

        return ranking

    def bulk_update_rankings_from_dataframe(self, dataframe):
        networks_db = self.all()

        dataframe["log_gamma_upper_confidence"] = np.round(
            (dataframe["log_gamma"] + 2 * dataframe["log_gamma_uncertainty"]) * 400 * log10(e), decimals=2
        )
        dataframe["log_gamma_lower_confidence"] = np.round(
            (dataframe["log_gamma"] - 2 * dataframe["log_gamma_uncertainty"]) * 400 * log10(e), decimals=2
        )

        for network_db in networks_db:
            network_db.log_gamma = dataframe.loc[network_db.id, "log_gamma"]
            network_db.log_gamma_uncertainty = dataframe.loc[network_db.id, "log_gamma_uncertainty"]
            network_db.log_gamma_upper_confidence = dataframe.loc[network_db.id, "log_gamma_upper_confidence"]
            network_db.log_gamma_lower_confidence = dataframe.loc[network_db.id, "log_gamma_lower_confidence"]

        self.bulk_update(networks_db, ["log_gamma", "log_gamma_uncertainty", "log_gamma_upper_confidence", "log_gamma_lower_confidence"])
