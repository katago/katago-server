from rest_framework.serializers import HyperlinkedModelSerializer

from katago_server.trainings.models import Network


class NetworkSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Network
        fields = '__all__'


class LimitedNetworkSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Network
        fields = ['url', 'uuid', 'model_file']
