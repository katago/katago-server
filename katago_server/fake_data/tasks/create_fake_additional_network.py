from config import celery_app
from katago_server.runs.models import Run

from katago_server.trainings.models import Network


@celery_app.task()
def create_fake_additional_network():
    current_run = Run.objects.select_current()
    last_network = Network.objects.filter(run=current_run).last()

    new_net = Network(parent_network_id=last_network.id, model_file="https://d3dndmfyhecmj0.cloudfront.net/g170/neuralnets/g170-b6c96-s175395328-d26788732.bin.gz", run=current_run)
    new_net.save()
