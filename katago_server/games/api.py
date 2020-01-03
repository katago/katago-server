from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from katago_server.contrib.permission import ReadOnly

from katago_server.games.models import RankingEstimationGame, TrainingGame
from katago_server.games.serializers import RankingEstimationGameCreateSerializer, RankingEstimationGameListSerializer, TrainingGameCreateSerializer, TrainingGameListSerializer


class RankingEstimationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows games to be uploaded or seen
    """
    queryset = RankingEstimationGame.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]

    # Used to get the proper serializer for the given action
    # so create still reference to an existing network
    # but display give nested details of the network
    def get_serializer_class(self):
        if self.action == 'create':
            return RankingEstimationGameCreateSerializer
        return RankingEstimationGameListSerializer


class TrainingEstimationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows games to be uploaded or seen
    """
    queryset = TrainingGame.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]

    # Used to get the proper serializer for the given action
    # so create still reference to an existing network
    # but display give nested details of the network
    def get_serializer_class(self):
        if self.action == 'create':
            return TrainingGameCreateSerializer
        return TrainingGameListSerializer
