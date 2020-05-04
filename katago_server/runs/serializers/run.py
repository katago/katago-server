import uuid as uuid
from rest_framework.fields import HiddenField
from rest_framework.serializers import HyperlinkedModelSerializer

from katago_server.runs.models import Run


class RunSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Run
        fields = (
            "url",
            "id",
            "created_at",
            "name",
            "data_board_len",
            "inputs_version",
            "max_search_threads_allowed",
            "rating_game_probability",
            "rating_game_high_elo_probability",
            "selfplay_client_config",
            "rating_client_config",
        )


