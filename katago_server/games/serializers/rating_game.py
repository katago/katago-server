from rest_framework.serializers import (
    HyperlinkedModelSerializer,
    HiddenField,
    CurrentUserDefault,
)

from katago_server.games.models import RatingGame
from katago_server.trainings.serializers import NetworkSerializerForTasks
from katago_server.users.serializers import LimitedUserSerializer


# Use as write only serializer
class RatingGameCreateSerializer(HyperlinkedModelSerializer):
    """
    RatingGameCreateSerializer serialize a new game adding the current user as submitter
    """

    # https://www.django-rest-framework.org/api-guide/validators/#advanced-field-defaults
    submitted_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = RatingGame
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
            "kg_game_uid",
        ]
        extra_kwargs = {
            "run": {"lookup_field": "name"},
            "white_network": {"lookup_field": "name"},
            "black_network": {"lookup_field": "name"},
        }


# Use as read only serializer
class RatingGameListSerializer(HyperlinkedModelSerializer):
    submitted_by = LimitedUserSerializer()
    white_network = NetworkSerializerForTasks()
    black_network = NetworkSerializerForTasks()

    class Meta:
        model = RatingGame
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
            "kg_game_uid",
        ]
        extra_kwargs = {
            "run": {"lookup_field": "name"},
            "white_network": {"lookup_field": "name"},
            "black_network": {"lookup_field": "name"},
        }
