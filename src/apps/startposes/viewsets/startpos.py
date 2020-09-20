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

