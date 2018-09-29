import pytest
from django.utils import timezone

from core.models import Bill, Record
from core.serializers import (
    BillSerializer,
    EndRecordSerializer,
    StartRecordSerializer,
)


@pytest.mark.django_db
class TestStartRecordSerializer:
    def test_record_is_valid(self):
        data = {
            'type': Record.START,
            'call_id': '42',
            'timestamp': timezone.now().isoformat(),
            'source': '99988526423',
            'destination': '9993468278'
        }
        serializer = StartRecordSerializer(data=data)

        assert serializer.is_valid()

    def test_create(self):
        self.call = '42'
        data = {
            'type': Record.START,
            'call_id': self.call,
            'timestamp': timezone.now().isoformat(),
            'source': '99988526423',
            'destination': '9993468278'
        }
        serializer = StartRecordSerializer(data=data)
        serializer.is_valid()
        assert serializer.save()


@pytest.mark.django_db
class TestEndRecordSerializer:
    def test_record_is_valid(self, make_start_record):
        start_record = make_start_record()
        data = {
            'type': Record.END,
            'call_id': start_record.call_id,
            'timestamp': timezone.now().isoformat()
        }
        serializer = EndRecordSerializer(data=data)

        assert serializer.is_valid()

    def test_method_create(self, make_start_record):
        start_record = make_start_record()
        data = {
            'type': Record.END,
            'call_id': start_record.call_id,
            'timestamp': timezone.now().isoformat(),
        }
        serializer = EndRecordSerializer(data=data)
        serializer.is_valid()
        assert serializer.save()


@pytest.mark.django_db
class TestBillSerializer:
    def test_bill_data(self, make_call_record):
        call_record = make_call_record()

        queryset = Bill.objects.filter(call__source=call_record.source)
        serializer = BillSerializer(queryset, many=True)

        data = serializer.data[0]
        assert data.__len__() == 5
        assert data['destination'] == '9993468278'
