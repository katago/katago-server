import logging
import random

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from katago_server.distributed_efforts.services import RatingNetworkPairerService
from katago_server.runs.models import Run
from katago_server.runs.serializers import RunSerializerForClient
from katago_server.trainings.models import Network
from katago_server.trainings.serializers import NetworkSerializerForTasks

logger = logging.getLogger(__name__)


class DistributedTaskViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # noinspection PyMethodMayBeStatic
    def create(self, request):
        current_run = Run.objects.select_current()
        serializer_context = {"request": request}  # Used by NetworkSerializer hyperlinked field to build and url ref
        run_content = RunSerializerForClient(current_run)

        if random.random() < current_run.rating_game_probability:
            pairer = RatingNetworkPairerService(current_run)
            pairing = pairer.generate_pairing()
            if pairing is not None:
                (white_network, black_network) = pairing
                white_network_content = NetworkSerializerForTasks(white_network, context=serializer_context)
                black_network_content = NetworkSerializerForTasks(black_network, context=serializer_context)
                response_body = {
                    "kind": "rating",
                    "run": run_content.data,
                    "config": current_run.rating_client_config,
                    "white_network": white_network_content.data,
                    "black_network": black_network_content.data,
                }
                return Response(response_body)

        best_network = Network.objects.select_best_without_uncertainty(current_run)
        if best_network is None:
            return Response({'error': 'No networks for run.'}, status=status.HTTP_404_NOT_FOUND)

        best_network_content = NetworkSerializerForTasks(best_network, context=serializer_context)
        response_body = {
            "kind": "selfplay",
            "run": run_content.data,
            "config": current_run.selfplay_client_config,
            "network": best_network_content.data,
        }
        return Response(response_body)
