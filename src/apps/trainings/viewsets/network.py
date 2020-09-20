from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from src.contrib.permission import ReadOnly

from src.apps.trainings.models import Network
from src.apps.trainings.serializers import NetworkSerializer


class NetworkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows networks to be viewed or edited.
    """

    queryset = Network.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = NetworkSerializer
    lookup_field = "name"
