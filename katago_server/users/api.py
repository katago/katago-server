
from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser

from katago_server.users.models import User
from katago_server.users.serializers import UserSerializer, GroupSerializer


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = GroupSerializer
