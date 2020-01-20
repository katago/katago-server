from config import celery_app

from katago_server.trainings.models import Network


@celery_app.task()
def create_fake_additional_network():
    last_network = Network.objects.last()

    new_net = Network(nb_blocks=6, nb_channels=125, parent_network_id=last_network.id, model_file="http://google.fr")
    new_net.save()
