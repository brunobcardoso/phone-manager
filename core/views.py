from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from core.serializers import StartRecordSerializer, EndRecordSerializer


class RecordViewSet(viewsets.ViewSet):
    """
    API endpoint that allow records to be created

    create:
    Create a start or end call record

    """
    def create(self, request):
        if request.data.get('type') == 'start':
            serializer = StartRecordSerializer(data=request.data)
        else:
            serializer = EndRecordSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
