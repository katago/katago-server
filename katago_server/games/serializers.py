from rest_framework.serializers import HyperlinkedModelSerializer, HiddenField, CurrentUserDefault

from katago_server.games.models import Game


class GameSerializer(HyperlinkedModelSerializer):
    # https://www.django-rest-framework.org/api-guide/validators/#advanced-field-defaults
    submitted_by = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Game
        fields = '__all__'
