import pytest
from django.utils import timezone

from core.models import Record, Call
from core.serializers import StartRecordSerializer, EndRecordSerializer


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
        assert Record.start_call_exists


@pytest.mark.django_db
class TestEndRecordSerializer:
    @pytest.fixture()
    def call(self):
        call = Call.objects.create(
            id='42',
            source='99988526423',
            destination='9993468278'
        )
        return call

    def test_record_is_valid(self, call):
        Record.objects.create(
            call=call,
            type=Record.START,
            timestamp=timezone.now().isoformat()
        )
        data = {
            'type': Record.END,
            'call_id': '42',
            'timestamp': timezone.now().isoformat()
        }
        serializer = EndRecordSerializer(data=data)

        assert serializer.is_valid()

    def test_create(self, call):
        Record.objects.create(
            call=call,
            type=Record.START,
            timestamp=timezone.now().isoformat()
        )
        self.call = '42'
        data = {
            'type': Record.END,
            'call_id': self.call,
            'timestamp': timezone.now().isoformat(),
        }
        serializer = EndRecordSerializer(data=data)
        serializer.is_valid()
        assert serializer.save()
        assert Record.start_call_exists
