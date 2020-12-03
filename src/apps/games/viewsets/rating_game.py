from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from src.contrib.permission import ReadOrAuthCreateOnly

from src.apps.games.models import RatingGame
from src.apps.games.serializers import (
    RatingGameCreateSerializer,
    RatingGameListSerializer,
)


class RatingGameViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows rating games to be uploaded or seen
    """

    queryset = RatingGame.objects.all()
    permission_classes = [IsAdminUser | ReadOrAuthCreateOnly]

    # Used to get the proper serializer for the given action
    # so create still reference to an existing network
    # but display give nested details of the network
    def get_serializer_class(self):
        if self.action == "create":
            return RatingGameCreateSerializer
        return RatingGameListSerializer
