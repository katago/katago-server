from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from katago_server.contrib.permission import ReadOnly

from katago_server.games.models import SelfPlay, Match
from katago_server.games.serializers import SelfPlaySerializer, MatchSerializer


class SelfPlayViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows self plays to be viewed or edited.
    """

    queryset = SelfPlay.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = SelfPlaySerializer


class MatchViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Match.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = MatchSerializer
