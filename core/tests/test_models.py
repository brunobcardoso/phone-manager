from decimal import Decimal

import pytest
from django.conf import settings
from django.core.validators import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
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
        with pytest.raises(expected_exception=DRFValidationError) as excinfo:
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
            timestamp='2016-02-29T12:02:00.0Z'
        )
        assert isinstance(record, Record)

    def test_record_str(self, make_start_record):
        record = make_start_record()
        assert record.__str__() == (f'{record.call}, {record.type}, '
                                    f'{record.timestamp}')

    def test_invalid_end_record_when_no_start_record(self, make_call):
        with pytest.raises(DRFValidationError) as excinfo:
            Record.objects.create(
                call=make_call(),
                type=Record.END,
                timestamp='2016-02-29T12:00:00.0Z'
            )
        assert 'There is no start record for this call' in str(excinfo)

    def test_invalid_end_record_timestamp(self, make_start_record):
        with pytest.raises(DRFValidationError) as excinfo:
            start_record = make_start_record(
                timestamp='2016-02-29T12:00:00.0Z'
            )

            Record.objects.create(
                call=start_record.call,
                type=Record.END,
                timestamp='2016-02-20T12:00:00.0Z'
            )
        error_msg = ('Timestamp of end record cannot be less or equal '
                     'to start record')
        assert error_msg in str(excinfo)

    def test_records_timestamps_cannot_be_equal(self, make_start_record):
        with pytest.raises(DRFValidationError) as excinfo:
            start_record = make_start_record(
                timestamp='2016-02-29T12:00:00.0Z'
            )

            Record.objects.create(
                call=start_record.call,
                type=Record.END,
                timestamp='2016-02-29T12:00:00.0Z'
            )
        error_msg = ('Timestamp of end record cannot be less or equal to'
                     ' start record')
        assert error_msg in str(excinfo)

    def test_unique_timestamp_for_source(self, make_call_record):
        with pytest.raises(DRFValidationError) as excinfo:
            make_call_record(
                id='42',
                source='99988526423',
                destination='9993468278',
                start_timestamp='2017-12-12T04:57:13Z',
                end_timestamp='2017-12-12T06:10:56Z'
            )
            make_call_record(
                id='43',
                source='99988526423',
                destination='9993468278',
                start_timestamp='2017-12-12T04:57:13Z',
                end_timestamp='2017-12-12T06:10:56Z'
            )
        error_msg = ('There is already a start record for this source and '
                     'timestamp')
        assert error_msg in str(excinfo)

    def test_unique_timestamp_for_destination(self, make_call_record):
        with pytest.raises(DRFValidationError) as excinfo:
            make_call_record(
                id='42',
                source='99988526456',
                destination='9993468278',
                start_timestamp='2017-12-12T04:57:13Z',
                end_timestamp='2017-12-12T06:10:56Z'
            )
            make_call_record(
                id='43',
                source='99988526423',
                destination='9993468278',
                start_timestamp='2017-12-12T04:57:13Z',
                end_timestamp='2017-12-12T06:10:56Z'
            )
        error_msg = ('There is already a start record for this destination '
                     'and timestamp')
        assert error_msg in str(excinfo)

@pytest.mark.django_db
class TestBillModel:
    def test_bill_creation(self, make_call_record):
        call_record = make_call_record(
            start_timestamp='2016-02-20T12:00:00.0Z',
            end_timestamp='2016-02-29T14:07:44.0Z'
        )
        bill = Bill.objects.get(call=call_record)
        assert isinstance(bill, Bill)
        assert bill.__str__() == (f'call_id: {call_record.id} '
                                  f'- price: {bill.price}')

    def test_duration_within_a_day(self, make_call_record):
        call_record = make_call_record(
            start_timestamp='2017-12-12T04:57:13Z',
            end_timestamp='2017-12-12T06:10:56Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = '1h13m43s'
        assert bill.duration == expected

    def test_duration_more_than_one_day(self, make_call_record):
        call_record = make_call_record(
            start_timestamp='2018-02-28T21:57:13Z',
            end_timestamp='2018-03-01T22:10:56Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = '24h13m43s'
        assert bill.duration == expected

    def test_total_minutes(self, make_call_record):
        call_record = make_call_record(
            start_timestamp='2017-12-12T04:57:13Z',
            end_timestamp='2017-12-12T06:10:56Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = 73
        assert bill.total_minutes == expected

    def test_standard_minutes_after_end_limit_hour(self, make_call_record):
        """
        Should not consider minutes after standard end limit hour
        """
        call_record = make_call_record(
            start_timestamp='2017-12-12T21:57:13Z',
            end_timestamp='2017-12-12T22:03:55Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = 2
        assert bill.standard_minutes() == expected

    def test_standard_minutes_before_start_limit_hour(self, make_call_record):
        """
        Should not consider minutes before standard start limit hour
        """
        call_record = make_call_record(
            start_timestamp='2017-12-12T05:57:13Z',
            end_timestamp='2017-12-12T06:05:13Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = 5
        assert bill.standard_minutes() == expected

    def test_standard_minutes_at_start_limit_hour(self, make_call_record):
        """
        Should consider the completed 60 seconds cycle when call start at
        start limit hour
        """
        call_record = make_call_record(
            start_timestamp='2018-02-28T06:00:00Z',
            end_timestamp='2018-02-28T06:01:50Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = 1
        assert bill.standard_minutes() == expected

    def test_standard_minutes_less_than_minute_cycle(self, make_call_record):
        """
        Should not consider if less than 60 seconds cycle
        """
        call_record = make_call_record(
            start_timestamp='2018-02-28T08:00:00Z',
            end_timestamp='2018-02-28T08:00:50Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = 0
        assert bill.standard_minutes() == expected

    def test_standard_minutes_between_sdt_start_limit(self, make_call_record):
        """
        Should consider only the completed minutes from the limit start to
        the end of the call.
        """
        call_record = make_call_record(
            start_timestamp='2017-12-12T04:57:13Z',
            end_timestamp='2017-12-12T06:10:56Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = 10
        assert bill.standard_minutes() == expected

    def test_standard_minutes_minute_cycle(self, make_call_record):
        """
        Should consider the completed 60 seconds cycle
        """
        call_record = make_call_record(
            start_timestamp='2017-12-12T21:00:13Z',
            end_timestamp='2017-12-12T21:10:13Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = 10
        assert bill.standard_minutes() == expected

    def test_standard_minutes_change_limits(self, make_call_record):
        """
        Should adapt to the new limits
        """
        call_record = make_call_record(
            start_timestamp='2017-12-12T11:57:26Z',
            end_timestamp='2017-12-12T12:10:13Z'
        )
        settings.STD_HOUR_START = 8
        settings.STD_HOUR_END = 12
        bill = Bill.objects.get(call=call_record)
        expected = 2
        assert bill.standard_minutes() == expected

    def test_standard_minutes_different_days(self, make_call_record):
        """
        Should consider the completed 60 seconds cycle
        """
        call_record = make_call_record(
            start_timestamp='2018-02-28T21:57:13Z',
            end_timestamp='2018-03-01T22:10:56Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = 961
        assert bill.standard_minutes() == expected

    def test_standing_charge_standard(self, make_call_record):
        call_record = make_call_record(
            start_timestamp='2017-12-12T06:00:00Z',
            end_timestamp='2017-12-12T21:10:13Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = 0.36
        assert bill.standing_charge() == expected

    def test_standing_charge_reduced(self, make_call_record):
        call_record = make_call_record(
            start_timestamp='2017-12-12T22:00:00Z',
            end_timestamp='2017-12-12T23:10:13Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = 0.36
        assert bill.standing_charge() == expected

    def test_calculate_price_all_standard(self, make_call_record):
        call_record = make_call_record(
            start_timestamp='2017-12-12T11:00:00Z',
            end_timestamp='2017-12-12T11:05:00Z'
        )
        bill = Bill.objects.get(call=call_record)
        tariff = Decimal('0.36')
        price_minute = Decimal('5') * Decimal('0.09')
        expected = round(tariff + price_minute, 2)
        assert bill.price == expected

    def test_calculate_price_all_reduced(self, make_call_record):
        call_record = make_call_record(
            start_timestamp='2017-12-12T22:00:00Z',
            end_timestamp='2017-12-12T23:05:00Z'
        )
        bill = Bill.objects.get(call=call_record)
        expected = Decimal('0.36')
        assert bill.price == expected
