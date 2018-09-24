import pytest
from django.utils import timezone

from core.models import Record
from core.serializers import StartRecordSerializer


@pytest.mark.django_db
class TestStartRecordSerializer:
    def test_record_is_valid(self):
        data = {
            'type': Record.START,
            'call_id': '42',
            'timestamp': '2016-02-29T12:00:00Z',
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
            'timestamp': timezone.now(),
            'source': '99988526423',
            'destination': '9993468278'
        }
        serializer = StartRecordSerializer(data=data)
        serializer.is_valid()
        assert serializer.save()
        assert Record.start_call_exists
