from rest_framework import serializers

from katago_server.distributed_efforts.models import PredefinedJob


class PredefinedJobModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredefinedJob
        fields = '__all__'

