from django.core.exceptions import ValidationError
from rest_framework.serializers import CurrentUserDefault, HiddenField, HyperlinkedModelSerializer

from src.apps.games.models import RatingGame
from src.apps.runs.models import Run
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

    def validate(self, data):
        if data["white_network"] == data["black_network"]:
            raise ValidationError("Ratings games cannot be between a network and itself")
        if not data["white_network"].rating_games_enabled or not data["black_network"].rating_games_enabled:
            raise ValidationError("Network is no longer enabled for rating games")
        if data["run"].status != Run.RunStatus.ACTIVE:
            raise ValidationError("Run is not active")
        if not data["submitted_by"]:
            raise ValidationError("Unknown user")
        if not data["run"].is_allowed_username(data["submitted_by"].username):
            raise ValidationError("Run is currently closed except for private testing")
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
