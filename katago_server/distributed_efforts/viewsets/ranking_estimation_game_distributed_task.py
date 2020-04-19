from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from katago_server.contrib.permission import ReadOnly
from katago_server.distributed_efforts.models import RankingEstimationGameDistributedTask
from katago_server.distributed_efforts.serializers import RankingEstimationGameDistributedTaskSerializer


class RankingEstimationGameDistributedTaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows runs to be viewed or edited.
    """

    queryset = RankingEstimationGameDistributedTask.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = RankingEstimationGameDistributedTaskSerializer
