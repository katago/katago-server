from celery.signals import worker_ready

from .create_fake_initial import create_fake_initial
from .create_fake_additional_network import create_fake_additional_network
from .create_fake_ranking_estimation_games import create_fake_ranking_estimation_games
from .create_fake_training_games import create_fake_training_games


@worker_ready.connect
def on_worker_ready(_sender=None, _conf=None, **_kwargs):
    create_fake_initial.delay()
