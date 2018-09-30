import re

from django.utils.timezone import timedelta, now
from rest_framework import status
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core import schemas
from core.models import Bill
from core.serializers import (
    BillSerializer,
    EndRecordSerializer,
    StartRecordSerializer
)


class RecordCreate(APIView):
    """
    Creates a start or end call record.
    """

    schema = schemas.get_record_schema()

    def post(self, request):
        if request.data.get('type') == 'start':
            serializer = StartRecordSerializer(data=request.data)
        else:
            serializer = EndRecordSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillList(APIView):
    """
    Retrieves the monthly bills for a given telephone number
    """

    schema = schemas.get_bill_schema()

    def get(self, request, subscriber):
        reference = request.GET.get('reference')
        last_closed_period = now().replace(day=1) - timedelta(days=1)

        if reference:
            try:
                month, year = map(int, re.split('[^\d]', reference))
                ref_date = now().replace(year=year, month=month)
            except ValueError:
                message = ('Invalid reference period format. Try one of the '
                           'following: MM/YYYY, MM-YYYY, MM:YYYY, MM.YYYY '
                           'where MM is the month and YYYY is the year.')
                raise ParseError(detail=message)

            if ref_date > last_closed_period:
                message = ('Invalid reference period. It\'s only possible to '
                           'get a telephone bill after the reference period '
                           'has ended.')
                raise ValidationError(detail=message)
        else:
            month, year = last_closed_period.month, last_closed_period.year

        queryset = Bill.objects.get_bills(source=subscriber, m=month, y=year)
        serializer = BillSerializer(queryset, many=True)

        response_data = {
            'subscriber': subscriber,
            'reference_period': f'{month:02d}/{year}',
            'bill_call_records': serializer.data
        }

        return Response(response_data)
