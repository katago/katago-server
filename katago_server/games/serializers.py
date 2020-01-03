from rest_framework.serializers import HyperlinkedModelSerializer, HiddenField, CurrentUserDefault, HyperlinkedRelatedField

from katago_server.games.models import RankingEstimationGame, TrainingGame
from katago_server.trainings.serializers import LimitedNetworkSerializer
from katago_server.users.serializers import LimitedUserSerializer


# Use as write only serializer
class RankingEstimationGameCreateSerializer(HyperlinkedModelSerializer):
    # https://www.django-rest-framework.org/api-guide/validators/#advanced-field-defaults
    submitted_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = RankingEstimationGame
        fields = '__all__'


# Use as read only serializer
class RankingEstimationGameListSerializer(HyperlinkedModelSerializer):
    submitted_by = LimitedUserSerializer()
    white_network = LimitedNetworkSerializer()
    black_network = LimitedNetworkSerializer()

    class Meta:
        model = RankingEstimationGame
        fields = '__all__'


# Use as write only serializer
class TrainingGameCreateSerializer(HyperlinkedModelSerializer):
    # https://www.django-rest-framework.org/api-guide/validators/#advanced-field-defaults
    submitted_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = TrainingGame
        fields = '__all__'


# Use as read only serializer
class TrainingGameListSerializer(HyperlinkedModelSerializer):
    submitted_by = LimitedUserSerializer()
    white_network = LimitedNetworkSerializer()
    black_network = LimitedNetworkSerializer()

    class Meta:
        model = TrainingGame
        fields = '__all__'
