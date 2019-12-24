from rest_framework.serializers import HyperlinkedModelSerializer

from katago_server.trainings.models import Network, Gating


class NetworkSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Network
        fields = '__all__'


class GatingSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Gating
        fields = '__all__'
