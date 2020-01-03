import random

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from katago_server.distributed_efforts.models import PredefinedJob, PredefinedJobStatus
from katago_server.distributed_efforts.serializers import PredefinedJobModelSerializer

import logging

logger = logging.getLogger(__name__)


def should_consume_predefined_job():
    return True
    return random.random() < 0.8


class JobViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def get_jobs(self, request):
        predefined_job_instance = PredefinedJob.objects.select_for_update(skip_locked=True)\
            .filter(status=PredefinedJobStatus.UP_FOR_GRAB.value)\
            .first()

        logger.warning(predefined_job_instance)

        if should_consume_predefined_job() and predefined_job_instance is not None:
            with transaction.atomic():
                predefined_job_instance.status = PredefinedJobStatus.ONGOING.value
                predefined_job_instance.assigned_to = request.user
                predefined_job_instance.assigned_at = timezone.now()
                predefined_job_instance.expire_at = timezone.now() + timezone.timedelta(hours=1)
                predefined_job_instance.save()

            predefined_job_content = PredefinedJobModelSerializer(predefined_job_instance)
            return Response({"kind": "PREDEFINED", "content": predefined_job_content.data})

        return Response({"kind": "DYNAMIC"})
