import uuid as uuid

from rest_framework.serializers import HyperlinkedModelSerializer, HiddenField, CurrentUserDefault

from katago_server.games.models import RankingEstimationGame
from katago_server.trainings.serializers import NetworkSerializerForTasks
from katago_server.users.serializers import LimitedUserSerializer


# Use as write only serializer
class RankingEstimationGameCreateSerializer(HyperlinkedModelSerializer):
    # https://www.django-rest-framework.org/api-guide/validators/#advanced-field-defaults
    submitted_by = HiddenField(default=CurrentUserDefault())
    uuid = HiddenField(default=uuid.uuid4())

    class Meta:
        model = RankingEstimationGame
        fields = "__all__"


# Use as read only serializer
class RankingEstimationGameListSerializer(HyperlinkedModelSerializer):
    submitted_by = LimitedUserSerializer()
    white_network = NetworkSerializerForTasks()
    black_network = NetworkSerializerForTasks()

    class Meta:
        model = RankingEstimationGame
        fields = "__all__"
