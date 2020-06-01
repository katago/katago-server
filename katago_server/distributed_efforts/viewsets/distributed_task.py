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
        if current_run is None:
            return Response({"error": "No active run."}, status=404)

        git_revision_hash_whitelist = current_run.git_revision_hash_whitelist
        git_revision_hash_whitelist = [s.strip().lower() for s in git_revision_hash_whitelist.replace(" ",",").split(",")]
        git_revision_hash_whitelist = [s for s in git_revision_hash_whitelist if len(s) > 0]
        git_revision = request.POST["git_revision"].strip().lower() if "git_revision" in request.POST else ""
        # Git revision hashes are 32 chars
        if len(git_revision) != 32:
            return Response(
                {"error": "This version of KataGo is not usable for distributed because either it's had custom modifications or has been compiled without version info."},
                status=400,
            )
        elif git_revision not in git_revision_hash_whitelist:
            return Response(
                {"error": "This version of KataGo is not enabled for distributed. If this is an official version and/or you think this is an oversight, please ask server admins to enable the following version hash: " + git_revision},
                status=400,
            )

        serializer_context = {"request": request}  # Used by NetworkSerializer hyperlinked field to build and url ref
        run_content = RunSerializerForClient(current_run, context=serializer_context)

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
            return Response({"error": "No networks for run."}, status=400)

        best_network_content = NetworkSerializerForTasks(best_network, context=serializer_context)
        response_body = {
            "kind": "selfplay",
            "run": run_content.data,
            "config": current_run.selfplay_client_config,
            "network": best_network_content.data,
        }
        return Response(response_body)
