from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from katago_server.contrib.permission import ReadOnly

from katago_server.trainings.models import Gating, Network
from katago_server.trainings.serializers import NetworkSerializer, GatingSerializer


class NetworkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows self plays to be viewed or edited.
    """

    queryset = Network.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = NetworkSerializer


class GatingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Gating.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = Gating
