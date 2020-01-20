from rest_framework import serializers

from katago_server.distributed_efforts.models import TrainingGameDistributedTask


class TrainingGameDistributedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingGameDistributedTask
        fields = "__all__"
