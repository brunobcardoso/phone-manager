from django.utils import timezone

from core.models import Record
from core.serializers import StartRecordSerializer


def test_record_is_valid():
    data = {
        'type': Record.START,
        'call_id': '42',
        'timestamp': timezone.now().isoformat(),
        'source': '99988526423',
        'destination': '9933468278'
    }
    serializer = StartRecordSerializer(data=data)

    assert serializer.is_valid()


def test_create():
    data = {
        'type': Record.START,
        'call_id': '42',
        'timestamp': timezone.now().isoformat(),
        'source': '99988526423',
        'destination': '9933468278'
    }
    serializer = StartRecordSerializer(data=data)
    serializer.is_valid()
    assert serializer.save()
