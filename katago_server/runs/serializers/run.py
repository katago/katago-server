from rest_framework.serializers import HyperlinkedModelSerializer

from katago_server.runs.models import Run


class RunSerializer(HyperlinkedModelSerializer):
    """
    RunSerializer serializes one or several run for create, list and detail display on the api
    """
    class Meta:
        model = Run
        fields = [
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
        ]


# TODO: what about naming it RunTasksSerializer for consistency with NetworkSerializerForTasks
class RunClientSerializer(HyperlinkedModelSerializer):
    """
    RunClientSerializer serializes a single run (the current one) inside a task
    """
    class Meta:
        model = Run
        fields = [
            "url",
            "name",
            "data_board_len",
            "inputs_version",
            "max_search_threads_allowed",
        ]


