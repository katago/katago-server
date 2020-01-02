from rest_framework.serializers import HyperlinkedModelSerializer, HiddenField, CurrentUserDefault, HyperlinkedRelatedField

from katago_server.games.models import Game
from katago_server.trainings.serializers import LimitedNetworkSerializer
from katago_server.users.serializers import LimitedUserSerializer


# Use as write only serializer
class GameCreateSerializer(HyperlinkedModelSerializer):
    # https://www.django-rest-framework.org/api-guide/validators/#advanced-field-defaults
    submitted_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Game
        fields = '__all__'


# Use as read only serializer
class GameListSerializer(HyperlinkedModelSerializer):
    submitted_by = LimitedUserSerializer()
    white_network = LimitedNetworkSerializer()
    black_network = LimitedNetworkSerializer()

    class Meta:
        model = Game
        fields = '__all__'
