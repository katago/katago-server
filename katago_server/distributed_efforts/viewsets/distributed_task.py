from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from katago_server.distributed_efforts.models import (
    RankingEstimationGameDistributedTask,
    TrainingGameDistributedTask,
    DynamicDistributedTaskConfiguration,
)
from katago_server.distributed_efforts.serializers import (
    RankingEstimationGameDistributedTaskSerializer,
    TrainingGameDistributedTaskSerializer,
    DynamicDistributedTaskKatagoConfigurationSerializer,
)

import logging

from katago_server.runs.models import Run
from katago_server.trainings.models import Network
from katago_server.trainings.serializers import NetworkSerializerForTasks

logger = logging.getLogger(__name__)


class DistributedTaskViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # noinspection PyMethodMayBeStatic
    def create(self, request):
        current_run = Run.objects.select_current()
        task_configuration = DynamicDistributedTaskConfiguration.get_solo()

        with transaction.atomic():
            ranking_distributed_task = RankingEstimationGameDistributedTask.objects.get_one_unassigned_with_lock(current_run)
            logger.info(f"ranking_distributed_task: {ranking_distributed_task}")
            should_play_predefined_ranking = task_configuration.should_play_predefined_ranking_game() and ranking_distributed_task is not None

            if should_play_predefined_ranking:
                ranking_distributed_task.assign_to(request.user)
                config_content = DynamicDistributedTaskKatagoConfigurationSerializer(task_configuration)
                distributed_task_content = RankingEstimationGameDistributedTaskSerializer(ranking_distributed_task)
                response_body = {
                    "type": "static",
                    "kind": "ranking",
                    "config": config_content.data.get("rating_katago_config"),
                    "content": distributed_task_content.data
                }
                return Response(response_body)

            # training_distributed_task = TrainingGameDistributedTask.objects.get_one_unassigned_with_lock()
            # logger.info('training_distributed_task', training_distributed_task)
            # should_play_predefined_training = task_configuration.should_play_predefined_training_game() and training_distributed_task is not None
            #
            # if should_play_predefined_training:
            #     training_distributed_task.assign_to(request.user)
            #     distributed_task_content = TrainingGameDistributedTaskSerializer(training_distributed_task)
            #     response_body = {"type": "static", "kind": "training", "content": distributed_task_content.data}
            #     return Response(response_body)

        serializer_context = {"request": request}  # Used by NetworkSerializer hyperlinked field to build and url ref
        config_content = DynamicDistributedTaskKatagoConfigurationSerializer(task_configuration)
        logger.info(f"config_content: {config_content}")
        best_network = Network.objects.select_best_without_uncertainty(current_run)
        logger.info(f"best_network: {best_network}")
        network_content = NetworkSerializerForTasks(best_network, context=serializer_context)
        response_body = {
            "type": "dynamic",
            "kind": "training",
            # TODO would this be the right way to include the current run's name?
            # "run": current_run.name,
            "config": config_content.data.get("selfplay_katago_config"),
            "network": network_content.data
            # TODO: Why do we have a "content": distributed_task_content.data above but not here?
        }
        return Response(response_body)
