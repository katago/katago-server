from rest_framework import serializers

from katago_server.distributed_efforts.models import DynamicDistributedTaskConfiguration


class DynamicDistributedTaskKatagoConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicDistributedTaskConfiguration
        fields = 'katago_config'
