from rest_framework import serializers

from katago_server.distributed_efforts.models import RankingEstimationGameDistributedTask


class RankingEstimationGameDistributedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RankingEstimationGameDistributedTask
        fields = "__all__"
