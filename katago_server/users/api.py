
from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from katago_server.contrib.permission import ReadOnly
from katago_server.users.models import User
from katago_server.users.serializers import GroupSerializer, FullUserSerializer, LimitedUserSerializer


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


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = GroupSerializer
