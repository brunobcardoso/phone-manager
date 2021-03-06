from decimal import Decimal

from django.conf import settings

from core.models import Bill


def test_bill_creation(make_call_record):
    call_record = make_call_record(
        start_timestamp='2016-02-20T12:00:00.0Z',
        end_timestamp='2016-02-29T14:07:44.0Z'
    )
    bill = Bill.objects.get(call=call_record)
    assert isinstance(bill, Bill)
    assert bill.__str__() == (f'call_id: {call_record.id} '
                              f'- price: {bill.price}')


def test_duration_within_a_day(make_call_record):
    call_record = make_call_record(
        start_timestamp='2017-12-12T04:57:13Z',
        end_timestamp='2017-12-12T06:10:56Z'
    )
    bill = Bill.objects.get(call=call_record)
    expected = '1h13m43s'
    assert bill.duration == expected


def test_duration_more_than_one_day(make_call_record):
    call_record = make_call_record(
        start_timestamp='2018-02-28T21:57:13Z',
        end_timestamp='2018-03-01T22:10:56Z'
    )
    bill = Bill.objects.get(call=call_record)
    expected = '24h13m43s'
    assert bill.duration == expected


def test_total_minutes(make_call_record):
    call_record = make_call_record(
        start_timestamp='2017-12-12T04:57:13Z',
        end_timestamp='2017-12-12T06:10:56Z'
    )
    bill = Bill.objects.get(call=call_record)
    expected = 73
    assert bill.total_minutes == expected


def test_standard_minutes_after_end_limit_hour(make_call_record):
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


def test_standard_minutes_before_start_limit_hour(make_call_record):
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


def test_standard_minutes_at_start_limit_hour(make_call_record):
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


def test_standard_minutes_less_than_minute_cycle(make_call_record):
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


def test_standard_minutes_between_sdt_start_limit(make_call_record):
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


def test_standard_minutes_minute_cycle(make_call_record):
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


def test_standard_minutes_change_limits(make_call_record):
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


def test_standard_minutes_different_days(make_call_record):
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


def test_standing_charge_standard(make_call_record):
    call_record = make_call_record(
        start_timestamp='2017-12-12T06:00:00Z',
        end_timestamp='2017-12-12T21:10:13Z'
    )
    bill = Bill.objects.get(call=call_record)
    expected = 0.36
    assert bill.standing_charge() == expected


def test_standing_charge_reduced(make_call_record):
    call_record = make_call_record(
        start_timestamp='2017-12-12T22:00:00Z',
        end_timestamp='2017-12-12T23:10:13Z'
    )
    bill = Bill.objects.get(call=call_record)
    expected = 0.36
    assert bill.standing_charge() == expected


def test_calculate_price_all_standard(make_call_record):
    call_record = make_call_record(
        start_timestamp='2017-12-12T11:00:00Z',
        end_timestamp='2017-12-12T11:05:00Z'
    )
    bill = Bill.objects.get(call=call_record)
    tariff = Decimal('0.36')
    price_minute = Decimal('5') * Decimal('0.09')
    expected = round(tariff + price_minute, 2)
    assert bill.price == expected


def test_calculate_price_all_reduced(make_call_record):
    call_record = make_call_record(
        start_timestamp='2017-12-12T22:00:00Z',
        end_timestamp='2017-12-12T23:05:00Z'
    )
    bill = Bill.objects.get(call=call_record)
    expected = Decimal('0.36')
    assert bill.price == expected
