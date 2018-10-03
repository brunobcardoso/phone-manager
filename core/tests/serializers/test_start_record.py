import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError as DRFValidationError

from core.models import Record, Call
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


def test_create_atomicity(make_call_record):
    with pytest.raises(DRFValidationError) as excinfo:
        make_call_record(
            id='42',
            start_timestamp='2016-02-29T12:02:00.0Z',
            end_timestamp='2016-02-29T12:02:05.0Z',
            source='99988526423',
            destination='9933468278'
        )
        data = {
            'type': Record.START,
            'call_id': '43',
            'timestamp': '2016-02-29T12:02:00.0Z',
            'source': '99988526423',
            'destination': '9933468278'
        }
        serializer = StartRecordSerializer(data=data)
        serializer.is_valid()
        serializer.save()
    error = 'There is already a start record for this source and timestamp'
    assert error in str(excinfo.value)
    assert Call.objects.count() == 1
