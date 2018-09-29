from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers import StartRecordSerializer, EndRecordSerializer


class RecordCreate(APIView):
    """
    API endpoint that allow records to be created
    """

    def post(self, request):
        if request.data.get('type') == 'start':
            serializer = StartRecordSerializer(data=request.data)
        else:
            serializer = EndRecordSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
