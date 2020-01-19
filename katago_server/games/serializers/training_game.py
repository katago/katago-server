import uuid as uuid

from rest_framework.serializers import HyperlinkedModelSerializer, HiddenField, CurrentUserDefault

from katago_server.games.models import TrainingGame
from katago_server.trainings.serializers import LimitedNetworkSerializer
from katago_server.users.serializers import LimitedUserSerializer


# Use as write only serializer
class TrainingGameCreateSerializer(HyperlinkedModelSerializer):
    # https://www.django-rest-framework.org/api-guide/validators/#advanced-field-defaults
    submitted_by = HiddenField(default=CurrentUserDefault())
    uuid = HiddenField(default=uuid.uuid4())

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
