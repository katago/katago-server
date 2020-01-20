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

from katago_server.trainings.models import Network
from katago_server.trainings.serializers import LimitedNetworkSerializer

logger = logging.getLogger(__name__)


class DistributedTaskViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, _request):
        kind = self.request.query_params.get("kind", None)

        if kind == "training":
            training_queryset = TrainingGameDistributedTask.objects.all()
            training_serializer = TrainingGameDistributedTaskSerializer(training_queryset, many=True)
            return Response(training_serializer.data)
        if kind == "ranking":
            ranking_queryset = RankingEstimationGameDistributedTask.objects.all()
            ranking_serializer = RankingEstimationGameDistributedTaskSerializer(ranking_queryset, many=True)
            return Response(ranking_serializer.data)

        training_queryset = TrainingGameDistributedTask.objects.all()
        training_serializer = TrainingGameDistributedTaskSerializer(training_queryset, many=True)
        ranking_queryset = RankingEstimationGameDistributedTask.objects.all()
        ranking_serializer = RankingEstimationGameDistributedTaskSerializer(ranking_queryset, many=True)
        return Response({"ranking": ranking_serializer.data, "training": training_serializer.data})

    @action(detail=False, methods=["post"])
    def get_job(self, request):
        task_configuration = DynamicDistributedTaskConfiguration.get_solo()

        with transaction.atomic():
            ranking_distributed_task = RankingEstimationGameDistributedTask.objects.get_one_unassigned_with_lock()
            training_distributed_task = TrainingGameDistributedTask.objects.get_one_unassigned_with_lock()

            should_play_predefined_ranking = task_configuration.should_play_predefined_ranking_game() and ranking_distributed_task is not None
            should_play_predefined_training = task_configuration.should_play_predefined_training_game() and training_distributed_task is not None

            if should_play_predefined_ranking:
                ranking_distributed_task.assign_to(request.user)
                distributed_task_content = RankingEstimationGameDistributedTaskSerializer(ranking_distributed_task)
                response_body = {"type": "static", "kind": "ranking", "content": distributed_task_content.data}
                return Response(response_body)

            if should_play_predefined_training:
                training_distributed_task.assign_to(request.user)
                distributed_task_content = TrainingGameDistributedTaskSerializer(training_distributed_task)
                response_body = {"type": "static", "kind": "training", "content": distributed_task_content.data}
                return Response(response_body)

        serializer_context = {"request": request}  # Used by NetworkSerializer hyperlinked field to build and url ref
        config_content = DynamicDistributedTaskKatagoConfigurationSerializer(task_configuration)
        best_network = Network.objects.select_best_without_uncertainty()
        network_content = LimitedNetworkSerializer(best_network, context=serializer_context)
        response_body = {"type": "dynamic", "kind": "training", "config": config_content.data.get("katago_config"), "network": network_content.data}
        return Response(response_body)
