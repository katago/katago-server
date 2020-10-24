from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from django_filters import rest_framework as filters

from src.contrib.permission import ReadOnly

from src.apps.trainings.models import Network
from src.apps.trainings.serializers import NetworkSerializer, NetworkSerializerForElo


class NetworkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows networks to be viewed or edited.
    """

    queryset = Network.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = NetworkSerializer
    lookup_field = "name"


class NetworkViewSetForElo(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for getting Elo ratings from models
    """

    queryset = Network.objects.all()
    permission_classes = [ReadOnly]
    serializer_class = NetworkSerializerForElo
    lookup_field = "name"
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("run__name",)
    pagination_class = None
