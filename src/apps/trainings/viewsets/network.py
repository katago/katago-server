from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.runs.models import Run
from src.apps.trainings.models import Network
from src.apps.trainings.serializers import NetworkSerializer, NetworkSerializerForElo, NetworkSerializerForTasks
from src.contrib.permission import ReadOnly


class NetworkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows networks to be viewed or edited.
    """

    queryset = Network.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = NetworkSerializer
    lookup_field = "name"

    @action(detail=False, methods=["GET"])
    def newest_training(self, request):
        current_run = Run.objects.select_current()
        if current_run is None:
            return Response({"error": "No active run."}, status=404)

        try:
            network = Network.objects.select_most_recent(current_run,for_training_games=True)
            if not network:
                raise Network.DoesNotExist()
        except Network.DoesNotExist:
            return Response({"error": "No networks found for run enabled for training games."}, status=400)

        serializer_context = {"request": request}  # Used by serialize hyperlinked field to build and url ref
        serializer = NetworkSerializerForTasks(network, context=serializer_context)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def strongest(self, request):
        current_run = Run.objects.select_current()
        if current_run is None:
            return Response({"error": "No active run."}, status=404)
        try:
            strongest_network = Network.objects.select_strongest_confident(run=current_run)
            if not strongest_network:
              raise Network.DoesNotExist()
        except Network.DoesNotExist:
            return Response({"error": "No networks found for run enabled for training games."}, status=400)

        serializer_context = {"request": request}  # Used by serialize hyperlinked field to build and url ref
        serializer = NetworkSerializerForTasks(strongest_network, context=serializer_context)
        return Response(serializer.data)


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


