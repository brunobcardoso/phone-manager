from django.utils import timezone

from core.models import Record
from core.serializers import EndRecordSerializer


def test_record_is_valid(make_start_record):
    start_record = make_start_record()
    data = {
        'type': Record.END,
        'call_id': start_record.call_id,
        'timestamp': timezone.now().isoformat()
    }
    serializer = EndRecordSerializer(data=data)

    assert serializer.is_valid()


def test_method_create(make_start_record):
    start_record = make_start_record()
    data = {
        'type': Record.END,
        'call_id': start_record.call_id,
        'timestamp': timezone.now().isoformat(),
    }
    serializer = EndRecordSerializer(data=data)
    serializer.is_valid()
    assert serializer.save()
