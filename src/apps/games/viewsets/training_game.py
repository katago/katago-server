from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from src.contrib.permission import ReadOrCreateOnly

from src.apps.games.models import TrainingGame
from src.apps.games.serializers import (
    TrainingGameCreateSerializer,
    TrainingGameListSerializer,
)


class TrainingGameViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows training games to be uploaded or seen
    """

    queryset = TrainingGame.objects.all()
    permission_classes = [IsAdminUser | ReadOrCreateOnly]

    # Used to get the proper serializer for the given action
    # so create still reference to an existing network
    # but display give nested details of the network
    def get_serializer_class(self):
        if self.action == "create":
            return TrainingGameCreateSerializer
        return TrainingGameListSerializer
