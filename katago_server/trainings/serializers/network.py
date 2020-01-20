import uuid as uuid
from rest_framework.fields import HiddenField
from rest_framework.serializers import HyperlinkedModelSerializer

from katago_server.trainings.models import Network


class NetworkSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Network
        fields = ("uuid", "nb_blocks", "nb_channels", "model_architecture_details", "model_file", "parent_network")

    uuid = HiddenField(default=uuid.uuid4())


class LimitedNetworkSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Network
        fields = ["url", "uuid", "model_file"]
