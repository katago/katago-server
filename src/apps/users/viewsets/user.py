from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from src.apps.users.models import User
from src.apps.users.serializers import FullUserSerializer, LimitedUserSerializer
from src.contrib.permission import ReadOnly


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    permission_classes = [IsAdminUser | ReadOnly]

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return FullUserSerializer
        return LimitedUserSerializer
