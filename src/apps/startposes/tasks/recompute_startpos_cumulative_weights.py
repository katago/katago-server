import numpy as np

from src import celery_app
from src.apps.runs.models import Run
from src.apps.startposes.models import StartPos, StartPosCumWeightOnly


@celery_app.task()
def recompute_startpos_cumulative_weights():
    """
    Periodically recompute the cumulative weights of all startposes
    :return:
    """
    current_run = Run.objects.select_current()
    if current_run is None:
        return
    if not current_run.startpos_locked:
        raise Exception(
            "recompute_startpos_cumulative_weights should only be called after locking startposes for the run"
        )

    startpos_weights = StartPos.objects.order_by("id").values_list("id", "weight")
    cumulative_weights = np.cumsum([w[1] for w in startpos_weights])
    new_objects = [StartPosCumWeightOnly(x[0], x[1]) for x in zip((w[0] for w in startpos_weights), cumulative_weights)]

    StartPosCumWeightOnly.objects.bulk_update(new_objects, ["cumulative_weight"], batch_size=10000)
    current_run.refresh_from_db()
    if len(cumulative_weights) > 0:
        current_run.startpos_total_weight = cumulative_weights[len(cumulative_weights) - 1]
    current_run.save()
