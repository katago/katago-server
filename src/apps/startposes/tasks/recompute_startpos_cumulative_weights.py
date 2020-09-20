import numpy as np
from config import celery_app

from src.apps.runs.models import Run
from src.apps.startposes.models import StartPos, StartPosCumWeightOnly


@celery_app.task()
def recompute_startpos_cumulative_weights(for_tests=False):
    """
    Periodically recompute the cumulative weights of all startposes
    :return:
    """
    current_run = Run.objects.select_current()
    if current_run is None:
        return
    if not current_run.startpos_locked:
        raise Exception("recompute_startpos_cumulative_weights should only be called after locking startposes for the run")

    startpos_weights = StartPos.objects.values_list("id","weight")
    cumulative_weights = np.cumsum([w[1] for w in startpos_weights])
    new_objects = [ StartPosCumWeightOnly(x[0],x[1]) for x in zip((w[0] for w in startpos_weights), cumulative_weights) ]

    StartPosCumWeightOnly.objects.bulk_update(
        new_objects, ["cumulative_weight"], batch_size = 10000
    )


