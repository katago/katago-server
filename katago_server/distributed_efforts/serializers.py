from rest_framework import serializers

from katago_server.distributed_efforts.models import RankingEstimationGameDistributedTask, TrainingGameDistributedTask, DynamicDistributedTaskConfiguration


class RankingEstimationGameDistributedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RankingEstimationGameDistributedTask
        fields = '__all__'


class TrainingGameDistributedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingGameDistributedTask
        fields = '__all__'


class DynamicDistributedTaskConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicDistributedTaskConfiguration
        fields = '__all__'
