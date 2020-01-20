from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from katago_server.contrib.permission import ReadOnly

from katago_server.games.models import TrainingGame
from katago_server.games.serializers import TrainingGameCreateSerializer, TrainingGameListSerializer


class TrainingGameViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows games to be uploaded or seen
    """

    queryset = TrainingGame.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]

    # Used to get the proper serializer for the given action
    # so create still reference to an existing network
    # but display give nested details of the network
    def get_serializer_class(self):
        if self.action == "create":
            return TrainingGameCreateSerializer
        return TrainingGameListSerializer
