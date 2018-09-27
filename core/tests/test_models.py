import pytest
from django.core.validators import ValidationError

from core.models import Call, Record, Bill


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

    def test_source_and_destination_cannot_be_equal(self, make_call):
        with pytest.raises(expected_exception=ValidationError) as excinfo:
            make_call(
                source='99988526423',
                destination='99988526423'
            )
        assert 'Source and Destination cannot be equal' in str(excinfo)

    def test_invalid_phone_number_less_than_10_digits(self, make_call):
        with pytest.raises(ValidationError) as excinfo:
            make_call(
                source='99988526',
                destination='99988'
            )
        assert 'source' in str(excinfo)
        assert 'destination' in str(excinfo)
        assert 'Invalid phone number.' in str(excinfo)

    def test_invalid_phone_number_more_than_11_digits(self, make_call):
        with pytest.raises(ValidationError) as excinfo:
            make_call(
                source='9998852600000',
                destination='999885264230000'
            )
        assert 'source' in str(excinfo)
        assert 'destination' in str(excinfo)
        assert 'Invalid phone number.' in str(excinfo)

    def test_invalid_phone_number_format(self, make_call):
        with pytest.raises(ValidationError) as excinfo:
            make_call(
                source='darth vader',
                destination='luke skywalker'
            )
        assert 'source' in str(excinfo)
        assert 'destination' in str(excinfo)
        assert 'Invalid phone number.' in str(excinfo)


@pytest.mark.django_db
class TestRecord:
    def test_start_record_creation(self, make_call):
        record = Record.objects.create(
            call=make_call(),
            type=Record.START,
            timestamp='2016-02-29T12:00:00.0Z'
        )
        assert isinstance(record, Record)

    def test_end_record_creation(self, make_start_record):
        start_record = make_start_record('2016-02-29T12:00:00.0Z')
        record = Record.objects.create(
            call=start_record.call,
            type=Record.END,
            timestamp='2016-02-29T12:00:00.0Z'
        )
        assert isinstance(record, Record)

    def test_record_str(self, make_start_record):
        record = make_start_record()
        assert record.__str__() == (f'{record.call}, {record.type}, '
                                    f'{record.timestamp}')

    def test_invalid_end_record_when_no_start_record(self, make_call):
        with pytest.raises(ValidationError) as excinfo:
            Record.objects.create(
                call=make_call(),
                type=Record.END,
                timestamp='2016-02-29T12:00:00.0Z'
            )
        assert 'There is no start record for this call' in str(excinfo)

    def test_invalid_end_record_timestamp(self, make_start_record):
        with pytest.raises(ValidationError) as excinfo:
            start_record = make_start_record(
                timestamp='2016-02-29T12:00:00.0Z'
            )

            Record.objects.create(
                call=start_record.call,
                type=Record.END,
                timestamp='2016-02-20T12:00:00.0Z'
            )
        error_msg = 'Timestamp of end record cannot be less than start record'
        assert error_msg in str(excinfo)

@pytest.mark.django_db
class TestBillModel:
    def test_bill_creation(self, make_call_record):
        call_record = make_call_record(
            start_timestamp='2016-02-29T12:00:00.0Z',
            end_timestamp='2016-02-29T14:00:00.0Z'
        )
        bill = Bill.objects.create(call=call_record)
        assert isinstance(bill, Bill)
        assert bill.__str__() == (f'call_id: {call_record.id} '
                                  f'- price: {bill.price}')
