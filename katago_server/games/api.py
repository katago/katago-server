from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from katago_server.contrib.permission import ReadOnly

from katago_server.games.models import Game
from katago_server.games.serializers import GameSerializer


class GameViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows games to be uploaded or seen
    """

    queryset = Game.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = GameSerializer
