from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.translation import gettext_lazy as _

register = template.Library()

n_training_games_format = _("%s training games")
n_rating_games_format = _("%s rating games")
n_games_format = _("%s games")
n_training_rows_format = _("%s rows generated")

# Peformance hack to avoid calling block translate tons of times in template in a loop


@register.filter
def as_n_training_games_str(value):
    return n_training_games_format % intcomma(value)


@register.filter
def as_n_rating_games_str(value):
    return n_rating_games_format % intcomma(value)


@register.filter
def as_n_games_str(value):
    return n_games_format % intcomma(value)


@register.filter
def as_n_training_rows_str(value):
    return n_training_rows_format % intcomma(value)
