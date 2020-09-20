from django.core.exceptions import ValidationError
from rest_framework.serializers import (
    HyperlinkedModelSerializer,
    HiddenField,
    CurrentUserDefault,
)

from src.apps.games.models import TrainingGame, validate_game_npzdata
from src.apps.trainings.serializers import NetworkSerializerForTasks
from src.apps.users.serializers import LimitedUserSerializer


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
            "game_length",
            "white_network",
            "black_network",
            "sgf_file",
            "training_data_file",
            "num_training_rows",
            "kg_game_uid",
        ]
        extra_kwargs = {
            "run": {"lookup_field": "name"},
            "white_network": {"lookup_field": "name"},
            "black_network": {"lookup_field": "name"},
        }

    def validate(self,data):
        validate_game_npzdata(data["training_data_file"], data["run"])
        if not data["white_network"].training_games_enabled or not data["black_network"].training_games_enabled:
            raise ValidationError("Network is no longer enabled for training games")
        return data


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
            "game_length",
            "white_network",
            "black_network",
            "sgf_file",
            "training_data_file",
            "num_training_rows",
            "kg_game_uid",
        ]
        extra_kwargs = {
            "run": {"lookup_field": "name"},
            "white_network": {"lookup_field": "name"},
            "black_network": {"lookup_field": "name"},
        }
