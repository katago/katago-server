from rest_framework.serializers import HyperlinkedModelSerializer

from katago_server.games.models import Match, SelfPlay


class MatchSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'


class SelfPlaySerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SelfPlay
        fields = '__all__'
