from rest_framework.serializers import (
    HyperlinkedModelSerializer,
    HiddenField,
    CurrentUserDefault,
)

from src.apps.games.models import RatingGame
from src.apps.trainings.serializers import NetworkSerializerForTasks
from src.apps.users.serializers import LimitedUserSerializer


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
            "gametype",
            "rules",
            "extra_metadata",
            "winner",
            "score",
            "resigned",
            "game_length",
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

    def validate(self,data):
        if not data["white_network"].rating_games_enabled or not data["black_network"].rating_games_enabled:
            raise ValidationError("Network is no longer enabled for rating games")
        return data

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
            "gametype",
            "rules",
            "extra_metadata",
            "winner",
            "score",
            "resigned",
            "game_length",
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
