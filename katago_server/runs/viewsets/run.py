from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from katago_server.contrib.permission import ReadOnly

from katago_server.runs.models import Run
from katago_server.runs.serializers import RunSerializer, RunClientSerializer


class RunViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows runs to be viewed or edited.
    """

    queryset = Run.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = RunSerializer
    filterset_fields = ['status']


class RunClientViewSet(viewsets.ModelViewSet):
    """
    API endpoint that gives only the fields of a run that self-play clients need.
    """

    queryset = Run.objects.all()
    permission_classes = [ReadOnly]
    serializer_class = RunClientSerializer

