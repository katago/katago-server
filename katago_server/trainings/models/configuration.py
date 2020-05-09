from django.db.models import IntegerField
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel


class NetworkBayesianRatingConfiguration(SingletonModel):
    def __str__(self):
        return "Bayesian elo configuration"

    class Meta:
        verbose_name = "Bayesian elo configuration"

    number_of_iterations = IntegerField(_("number of iterations"), help_text=_("updating log_gamma is iterative"), default=10)
