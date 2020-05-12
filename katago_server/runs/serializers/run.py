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
            "selfplay_client_config",
            "rating_client_config",
        ]
        extra_kwargs = {
            "url": {"lookup_field": "name"},
        }


class RunSerializerForClient(HyperlinkedModelSerializer):
    """
    Serializer exposing only the fields of a run that a self-play client needs on startup.
    """

    class Meta:
        model = Run
        fields = [
            "id",
            "url",
            "name",
            "data_board_len",
            "inputs_version",
            "max_search_threads_allowed",
        ]
        extra_kwargs = {
            "url": {"lookup_field": "name"},
        }
