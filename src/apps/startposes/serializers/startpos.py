from rest_framework.serializers import HyperlinkedModelSerializer, ListSerializer
from django.core.exceptions import ValidationError

from src.apps.startposes.models import StartPos


class BulkStartPosSerializer(ListSerializer):
    """
    Serializer for uploading a large list of startposes all at once
    """

    def create(self, validated_data):
        result = [self.child.create(elt) for elt in validated_data]

        try:
            StartPos.objects.bulk_create(result,batch_size=1000)
        except IntegrityError as e:
            raise ValidationError(e)

        return result

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
            "run": {"lookup_field": "name"},
        }
        list_serializer_class = BulkStartPosSerializer


    def validate(self,data):
        if not data["run"]:
            raise ValidationError("Missing 'run' field for startpos")
        if not data["run"].startpos_locked:
            raise ValidationError("Can only upload while run startPoses are locked to prevent startpos races from clients.")
        return data


    def create(self, validated_data):
        instance = StartPos(**validated_data)

        # Don't save if it's a list of data, instead we rely on BulkStartPosSerializer which will bulk_create
        if not isinstance(self._kwargs["data"], list):
            instance.save()

        return instance
