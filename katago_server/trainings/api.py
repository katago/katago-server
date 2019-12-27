from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from katago_server.contrib.permission import ReadOnly

from katago_server.trainings.models import Network
from katago_server.trainings.serializers import NetworkSerializer


class NetworkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows self plays to be viewed or edited.
    """

    queryset = Network.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = NetworkSerializer

