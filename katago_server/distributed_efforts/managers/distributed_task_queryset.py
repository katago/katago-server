from django.db.models import QuerySet
from django.apps import apps


class DistributedTaskQuerySet(QuerySet):
    def get_one_unassigned_with_lock(self):
        AbstractDistributedTask = apps.get_model("distributed_efforts.AbstractDistributedTask")
        self.select_for_update(skip_locked=True).filter(status=AbstractDistributedTask.Status.UNASSIGNED).first()
