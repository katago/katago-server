from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from katago_server.contrib.permission import ReadOnly

from katago_server.runs.models import Run
from katago_server.runs.serializers import RunSerializer, RunSerializerForClient


class RunViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows runs to be viewed or edited.
    """

    queryset = Run.objects.all()
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = RunSerializer
    filterset_fields = ["status"]

    # https://stackoverflow.com/a/58168950
    @action(detail=False, methods=["GET"])
    def current(self, request):
        """
        API endpoint that gives only the fields of a run that self-play clients need.
        :return:
        """
        current_run = Run.objects.select_current()
        if current_run is None:
            return Response({'error': 'No active run.'}, status=status.HTTP_404_NOT_FOUND)
        self.kwargs["pk"] = current_run.pk
        return self.retrieve(request)

    @action(detail=False, methods=["GET"])
    def current_for_client(self, request):
        """
        API endpoint that gives only the fields of a run that self-play clients need.
        :return:
        """
        current_run = Run.objects.select_current()
        if current_run is None:
            return Response({'error': 'No active run.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(RunSerializerForClient(current_run,context={'request': request}).data)
