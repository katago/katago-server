from rest_framework.serializers import HyperlinkedModelSerializer

from src.apps.startposes.models import StartPos


class StartPosSerializer(HyperlinkedModelSerializer):
    """
    Serializer for upload of startposes.
    """

    class Meta:
        model = StartPos
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

    def validate(self,data):
        if not data["run"]:
            raise ValidationError("Missing 'run' field for startpos")
        if not data["run"].startpos_locked:
            raise ValidationError("Can only upload while run startPoses are locked to prevent startpos races from clients.")
        return data

