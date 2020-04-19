from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from katago_server.contrib.permission import ReadOnly
from katago_server.distributed_efforts.models import TrainingGameDistributedTask
from katago_server.distributed_efforts.serializers import TrainingGameDistributedTaskSerializer


class TrainingGameDistributedTaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows runs to be viewed or edited.
    """

    queryset = TrainingGameDistributedTask.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = TrainingGameDistributedTaskSerializer
