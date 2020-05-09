from rest_framework import serializers

from katago_server.users.models import User


class LimitedUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    LimitedUserSerializer does not leak user email. Non superuser uses this serializer.
    """

    class Meta:
        model = User
        fields = ["url", "username"]


class FullUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    LimitedUserSerializer display user email. Superuser uses this serializer.
    """

    class Meta:
        model = User
        fields = ["url", "username", "email"]
