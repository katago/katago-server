from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from src.apps.startposes.models import StartPos
from src.apps.startposes.serializers import StartPosSerializer


class StartPosViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows startposes to be uploaded.
    """

    queryset = StartPos.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = StartPosSerializer

    def get_serializer(self, *args, **kwargs):
        # Make it so that if the user is uploading a list of stuff instead of a single json object
        # we assume the user is giving us a list of json objects and wanting to do multiple creates.
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(StartPosViewSet, self).get_serializer(*args, **kwargs)
