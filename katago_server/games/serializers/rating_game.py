import uuid as uuid

from rest_framework.serializers import HyperlinkedModelSerializer, HiddenField, CurrentUserDefault

from katago_server.games.models import RatingGame
from katago_server.trainings.serializers import NetworkSerializerForTasks
from katago_server.users.serializers import LimitedUserSerializer


# Use as write only serializer
class RatingGameCreateSerializer(HyperlinkedModelSerializer):
    # https://www.django-rest-framework.org/api-guide/validators/#advanced-field-defaults
    submitted_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = RatingGame
        fields = "__all__"


# Use as read only serializer
class RatingGameListSerializer(HyperlinkedModelSerializer):
    submitted_by = LimitedUserSerializer()
    white_network = NetworkSerializerForTasks()
    black_network = NetworkSerializerForTasks()

    class Meta:
        model = RatingGame
        fields = "__all__"
