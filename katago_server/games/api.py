from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from katago_server.contrib.permission import ReadOnly

from katago_server.games.models import Game
from katago_server.games.serializers import GameCreateSerializer, GameListSerializer


class GameViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows games to be uploaded or seen
    """

    queryset = Game.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]

    # Used to get the proper serializer for the given action
    def get_serializer_class(self):
        if self.action == 'create':
            return GameCreateSerializer
        return GameListSerializer
