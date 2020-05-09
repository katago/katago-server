from rest_framework.serializers import (
    HyperlinkedModelSerializer,
    HiddenField,
    CurrentUserDefault,
)

from katago_server.games.models import TrainingGame
from katago_server.trainings.serializers import NetworkSerializerForTasks
from katago_server.users.serializers import LimitedUserSerializer


# Use as write only serializer
class TrainingGameCreateSerializer(HyperlinkedModelSerializer):
    """
    TrainingGameCreateSerializer serialize a new game adding the current user as submitter
    """

    # https://www.django-rest-framework.org/api-guide/validators/#advanced-field-defaults
    submitted_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = TrainingGame
        fields = [
            "url",
            "id",
            "run",
            "created_at",
            "submitted_by",
            "board_size_x",
            "board_size_y",
            "handicap",
            "komi",
            "rules",
            "extra_metadata",
            "winner",
            "score",
            "resigned",
            "white_network",
            "black_network",
            "sgf_file",
            "training_data_file",
            "kg_game_uid",
        ]


# Use as read only serializer
class TrainingGameListSerializer(HyperlinkedModelSerializer):
    submitted_by = LimitedUserSerializer()
    white_network = NetworkSerializerForTasks()
    black_network = NetworkSerializerForTasks()

    class Meta:
        model = TrainingGame
        fields = [
            "url",
            "id",
            "run",
            "created_at",
            "submitted_by",
            "board_size_x",
            "board_size_y",
            "handicap",
            "komi",
            "rules",
            "extra_metadata",
            "winner",
            "score",
            "resigned",
            "white_network",
            "black_network",
            "sgf_file",
            "training_data_file",
            "kg_game_uid",
        ]
