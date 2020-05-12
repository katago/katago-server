from rest_framework.serializers import HyperlinkedModelSerializer

from katago_server.trainings.models import Network


class NetworkSerializer(HyperlinkedModelSerializer):
    """
    Serializer for general display of networks for their info pages
    """

    class Meta:
        model = Network
        fields = [
            "url",
            "run",
            "name",
            "created_at",
            "network_size",
            "is_random",
            "model_file",
            "model_file_bytes",
            "model_file_sha256",
            "parent_network",
        ]
        extra_kwargs = {
            # "url": {"lookup_field": "name"},
            "run": {"lookup_field": "name"},
        }


class NetworkSerializerForTasks(HyperlinkedModelSerializer):
    """
    Serializer exposing only the fields of a network that a self-play client needs.
    """

    class Meta:
        model = Network
        fields = [
            "url",
            "run",
            "name",
            "created_at",
            "is_random",
            "model_file",
            "model_file_bytes",
            "model_file_sha256",
        ]
        extra_kwargs = {
            #"url": {"lookup_field": "name"},
            "run": {"lookup_field": "name"},
        }
