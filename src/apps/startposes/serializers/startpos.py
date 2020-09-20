from rest_framework.serializers import HyperlinkedModelSerializer

from src.apps.startposes.models import StartPos


class StartPosSerializer(HyperlinkedModelSerializer):
    """
    Serializer for upload of startposes.
    """

    class Meta:
        model = Network
        fields = [
            "url",
            "run",
            "created_at",
            "weight",
            "data",
        ]
        extra_kwargs = {
            "url": {"lookup_field": "name"},
            "run": {"lookup_field": "name"},
        }

