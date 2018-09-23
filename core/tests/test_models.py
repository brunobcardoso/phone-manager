import pytest

from core.models import Call, Record


@pytest.mark.django_db
class TestCall:
    def test_call_creation(self):
        call = Call.objects.create(id='42', source='99988526423', destination='9993468278')
        assert isinstance(call, Call)
        assert call.call_id == call.id
        assert call.__str__() == f'{call.id}, {call.source}, {call.destination}'


@pytest.mark.django_db
class TestRecord:

    def test_start_record_creation(self):
        call = Call.objects.create(id='42', source='99988526423', destination='9993468278')
        record = Record.objects.create(call=call, type=Record.START, timestamp='2016-02-29T12:00:00.0Z')
        assert isinstance(record, Record)

    def test_end_record_creation(self):
        call = Call.objects.create(id='42', source='99988526423', destination='9993468278')
        record = Record.objects.create(call=call, type=Record.END, timestamp='2016-02-29T12:00:00.0Z')
        assert isinstance(record, Record)

    def test_record_str(self):
        call = Call.objects.create(id='42', source='99988526423', destination='9993468278')
        record = Record.objects.create(call=call, type=Record.START, timestamp='2016-02-29T12:00:00.0Z')
        assert record.__str__() == f'{record.call}, {record.type}, {record.timestamp}'

    def test_record_start_call_exists(self):
        call = Call.objects.create(id='42', source='99988526423', destination='9993468278')
        Record.objects.create(call=call, type=Record.START, timestamp='2016-02-29T12:00:00.0Z')
        end_record = Record.objects.create(call=call, type=Record.END, timestamp='2016-02-29T12:00:00.0Z')
        assert end_record.start_call_exists
