import uuid as uuid
from rest_framework.fields import HiddenField
from rest_framework.serializers import HyperlinkedModelSerializer

from katago_server.runs.models import Run


class RunSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Run
        fields = ("url", "id", "created_at", "name")


