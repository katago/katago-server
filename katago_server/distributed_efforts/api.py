import random

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from katago_server.distributed_efforts.models import RankingEstimationGameDistributedTask, TrainingGameDistributedTask, DynamicDistributedTaskConfiguration
from katago_server.distributed_efforts.serializers import RankingEstimationGameDistributedTaskSerializer, TrainingGameDistributedTaskSerializer, DynamicDistributedTaskConfigurationSerializer

import logging

from katago_server.trainings.models import Network
from katago_server.trainings.serializers import LimitedNetworkSerializer

logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
class DistributedTaskViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        kind = self.request.query_params.get('kind', None)
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

    @action(detail=False, methods=['post'])
    def get_jobs(self, request):
        ranking_distributed_task_instance = RankingEstimationGameDistributedTask.objects.select_for_update(skip_locked=True).filter(status=RankingEstimationGameDistributedTask.Status.UNASSIGNED).first()
        training_distributed_task_instance = TrainingGameDistributedTask.objects.select_for_update(skip_locked=True).filter(status=TrainingGameDistributedTask.Status.UNASSIGNED).first()

        user_speed_index = self._user_compute_power_strength(request.user)

        if self._should_consume_ranking_distributed_task(request.user, user_speed_index) and ranking_distributed_task_instance is not None:
            self._assign_task(ranking_distributed_task_instance, request.user)
            distributed_task_content = RankingEstimationGameDistributedTaskSerializer(ranking_distributed_task_instance)
            return Response({"type": "static", "kind": "ranking", "content": distributed_task_content.data})

        if self._should_consume_training_distributed_task(request.user, user_speed_index) and training_distributed_task_instance is not None:
            self._assign_task(training_distributed_task_instance, request.user)
            distributed_task_content = TrainingGameDistributedTaskSerializer(training_distributed_task_instance)
            return Response({"type": "static", "kind": "training", "content": distributed_task_content.data})

        serializer_context = {'request': request}  # Used by NetworkSerializer hyperlinked field to build and url ref
        config_content = DynamicDistributedTaskConfigurationSerializer(DynamicDistributedTaskConfiguration.get_solo())
        network_content = LimitedNetworkSerializer(self._select_top_network(), context=serializer_context)
        return Response({"type": "dynamic", "kind": "training", "config": config_content.data.get("katago_config"), "network": network_content.data})

    @staticmethod
    def _user_compute_power_strength(user):
        # TODO: based on last X games Gflop, or duration(?) return a speed index S in [0, 10] that indicate if user is
        # TODO: ... the S_th decile of fastest user
        return 10

    @staticmethod
    def _should_consume_ranking_distributed_task(user, user_speed_index):
        if user_speed_index >= 9:  # very fast clients
            return random.random() < 0.8
        if user_speed_index >= 7:  # fast clients
            return random.random() < 0.1

        # For slower client, max one match at the same time
        return not RankingEstimationGameDistributedTask.objects.filter(assigned_to=user, status=RankingEstimationGameDistributedTask.Status.ONGOING).exist()

    @staticmethod
    def _should_consume_training_distributed_task(user, user_speed_index):
        return random.random() < 0.1

    @staticmethod
    def _assign_task(task_instance, target_user):
        with transaction.atomic():
            task_instance.status = RankingEstimationGameDistributedTask.Status.ONGOING
            task_instance.assigned_to = target_user
            task_instance.assigned_at = timezone.now()
            task_instance.expire_at = timezone.now() + timezone.timedelta(hours=1)
            task_instance.save()

    @staticmethod
    def _select_top_network():
        # TODO: maybe add a more complex strategy, where a good, but not best network has some chance to get selfplays
        return Network.objects.order_by("-log_gamma_upper_confidence").first()
