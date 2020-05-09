from rest_framework.serializers import HyperlinkedModelSerializer

from katago_server.trainings.models import Network


class NetworkSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Network
        fields = ["url", "run", "name", "created_at",
                  "network_size", "is_random", "model_file", "model_file_bytes", "model_file_sha256",
                  "parent_network"]


class NetworkSerializerForTasks(HyperlinkedModelSerializer):
    class Meta:
        model = Network
        fields = ["url", "run", "name", "created_at",
                  "is_random", "model_file", "model_file_bytes", "model_file_sha256"]
