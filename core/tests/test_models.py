import pytest
from django.core.validators import ValidationError

from core.models import Call, Record


@pytest.mark.django_db
class TestCall:
    def test_call_creation(self):
        call = Call.objects.create(
            id='42',
            source='99988526423',
            destination='9993468278')

        assert isinstance(call, Call)
        assert call.call_id == call.id
        assert call.__str__() == f'{call.id}'

    def test_source_and_destination_cannot_be_equal(self):
        with pytest.raises(expected_exception=ValidationError) as excinfo:
            Call.objects.create(
                id='42',
                source='99988526423',
                destination='99988526423'
            )
        assert 'Source and Destination cannot be equal' in str(excinfo)

    def test_invalid_phone_number_less_than_10_digits(self):
        with pytest.raises(ValidationError) as excinfo:
            Call.objects.create(
                id='42',
                source='999885269',
                destination='99988526423'
            )
        assert 'source' in str(excinfo)
        assert 'Invalid phone number.' in str(excinfo)

    def test_invalid_phone_number_more_than_11_digits(self):
        with pytest.raises(ValidationError) as excinfo:
            Call.objects.create(
                id='42',
                source='9998852600000',
                destination='99988526423'
            )
        assert 'source' in str(excinfo)
        assert 'Invalid phone number.' in str(excinfo)

    def test_invalid_phone_number_format(self):
        with pytest.raises(ValidationError) as excinfo:
            Call.objects.create(
                id='42',
                source='My phone',
                destination='99988526423'
            )
        assert 'source' in str(excinfo)
        assert 'Invalid phone number.' in str(excinfo)


@pytest.mark.django_db
class TestRecord:
    @pytest.fixture()
    def call(self):
        call = Call.objects.create(
            id='42',
            source='99988526423',
            destination='9993468278'
        )
        return call

    @pytest.fixture()
    def start_record(self, call):
        start_record = Record.objects.create(
            call=call,
            type=Record.START,
            timestamp='2016-02-29T12:00:00.0Z'
        )
        return start_record

    def test_start_record_creation(self, call):
        record = Record.objects.create(
            call=call,
            type=Record.START,
            timestamp='2016-02-29T12:00:00.0Z'
        )
        assert isinstance(record, Record)

    def test_end_record_creation(self, call, start_record):
        record = Record.objects.create(
            call=call,
            type=Record.END,
            timestamp='2016-02-29T12:00:00.0Z'
        )
        assert isinstance(record, Record)

    def test_record_str(self, call):
        record = Record.objects.create(
            call=call,
            type=Record.START,
            timestamp='2016-02-29T12:00:00.0Z'
        )
        assert record.__str__() == (f'{record.call}, {record.type}, '
                                    f'{record.timestamp}')

    def test_record_start_call_exists(self, call):
        Record.objects.create(
            call=call,
            type=Record.START,
            timestamp='2016-02-29T12:00:00.0Z'
        )
        end_record = Record.objects.create(
            call=call,
            type=Record.END,
            timestamp='2016-02-29T12:00:00.0Z'
        )
        assert end_record.start_call_exists

    def test_invalid_end_record_without_corresponding_start_record(self, call):
        with pytest.raises(ValidationError) as excinfo:
            record = Record.objects.create(
                call=call,
                type=Record.END,
                timestamp='2016-02-29T12:00:00.0Z'
            )
        assert 'There is no start record for this call' in str(excinfo)

    def test_invalid_end_record_timestamp(self, call):
        with pytest.raises(ValidationError) as excinfo:
            Record.objects.create(
                call=call,
                type=Record.START,
                timestamp='2016-02-29T12:00:00.0Z'
            )

            Record.objects.create(
                call=call,
                type=Record.END,
                timestamp='2016-02-20T12:00:00.0Z'
            )
        error_msg = 'Timestamp of end record cannot be less than start record'
        assert error_msg in str(excinfo)
