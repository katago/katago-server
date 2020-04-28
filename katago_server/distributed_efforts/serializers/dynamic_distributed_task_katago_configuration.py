from rest_framework import serializers

from katago_server.distributed_efforts.models import DynamicDistributedTaskConfiguration


class DynamicDistributedTaskKatagoConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicDistributedTaskConfiguration
        fields = ("selfplay_katago_config","rating_katago_config",)
