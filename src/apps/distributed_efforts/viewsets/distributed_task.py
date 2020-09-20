import logging
import random

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.apps.distributed_efforts.services import RatingNetworkPairerService
from src.apps.runs.models import Run
from src.apps.runs.serializers import RunSerializerForClient
from src.apps.trainings.models import Network
from src.apps.trainings.serializers import NetworkSerializerForTasks

logger = logging.getLogger(__name__)


class DistributedTaskViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # noinspection PyMethodMayBeStatic
    def create(self, request):
        current_run = Run.objects.select_current()
        if current_run is None:
            return Response({"error": "No active run."}, status=404)

        git_revision_hash_whitelist = current_run.git_revision_hash_whitelist
        git_revision_hash_whitelist = [s for s in git_revision_hash_whitelist.split("\n") if len(s) > 0]
        git_revision_hash_whitelist = [s.split("#")[0].strip().lower() for s in git_revision_hash_whitelist]
        git_revision_hash_whitelist = [s for s in git_revision_hash_whitelist if len(s) > 0]
        git_revision = request.data["git_revision"].strip().lower() if "git_revision" in request.data else ""
        # Git revision hashes are at least 40 chars, we can also optionally allow plus revisions and other stuff
        if len(git_revision) < 40:
            return Response(
                {"error": "This version of KataGo is not usable for distributed because either it's had custom modifications or has been compiled without version info."},
                status=400,
            )
        elif git_revision not in git_revision_hash_whitelist:
            return Response(
                {"error": "This version of KataGo is not enabled for distributed. If this is an official version and/or you think this is an oversight, please ask server admins to enable the following version hash: " + git_revision},
                status=400,
            )

        allow_rating_task = True
        allow_selfplay_task = True
        if "allow_rating_task" in request.data:
            allow_rating_task = request.data["allow_rating_task"].lower()
            if allow_rating_task == "true":
                allow_rating_task = True
            elif allow_rating_task == "false":
                allow_rating_task = False
            else:
                return Response({"error": "allow_rating_task was neither 'true' nor 'false'"},status=400)
        if "allow_selfplay_task" in request.data:
            allow_selfplay_task = request.data["allow_selfplay_task"].lower()
            if allow_selfplay_task == "true":
                allow_selfplay_task = True
            elif allow_selfplay_task == "false":
                allow_selfplay_task = False
            else:
                return Response({"error": "allow_selfplay_task was neither 'true' nor 'false'"},status=400)

        if not allow_rating_task and not allow_selfplay_task:
            return Response({"error": "allow_rating_task and allow_selfplay_task are both false"},status=400)

        task_rep_factor = 1
        if "task_rep_factor" in request.data:
            try:
                task_rep_factor = int(request.data["task_rep_factor"])
            except ValueError:
                return Response({"error": "task_rep_factor was not an integer from 1 to 64"},status=400)
            if task_rep_factor < 1 || task_rep_factor > 64:
                return Response({"error": "task_rep_factor was not an integer from 1 to 64"},status=400)

        serializer_context = {"request": request}  # Used by NetworkSerializer hyperlinked field to build and url ref
        run_content = RunSerializerForClient(current_run, context=serializer_context)

        if not allow_selfplay_task or (allow_rating_task and random.random() < current_run.rating_game_probability):
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

        try:
            best_network = Network.objects.select_most_recent(current_run,for_training_games=True)
            if best_network is None:
                return Response({"error": "No networks found for run enabled for training games."}, status=400)
        except Network.DoesNotExist:
            return Response({"error": "No networks found for run enabled for training games."}, status=400)

        best_network_content = NetworkSerializerForTasks(best_network, context=serializer_context)
        response_body = {
            "kind": "selfplay",
            "run": run_content.data,
            "config": current_run.selfplay_client_config,
            "network": best_network_content.data,
        }
        return Response(response_body)
