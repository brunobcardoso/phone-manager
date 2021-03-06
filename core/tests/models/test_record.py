import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from core.models import Record


def test_start_record_creation(make_call):
    record = Record.objects.create(
        call=make_call(),
        type=Record.START,
        timestamp='2016-02-29T12:00:00.0Z'
    )
    assert isinstance(record, Record)


def test_end_record_creation(make_start_record):
    start_record = make_start_record('2016-02-29T12:00:00.0Z')
    record = Record.objects.create(
        call=start_record.call,
        type=Record.END,
        timestamp='2016-02-29T12:02:00.0Z'
    )
    assert isinstance(record, Record)


def test_record_str(make_start_record):
    record = make_start_record()
    assert record.__str__() == (f'{record.call}, {record.type}, '
                                f'{record.timestamp}')


def test_invalid_end_record_when_no_start_record(make_call):
    with pytest.raises(DRFValidationError) as excinfo:
        Record.objects.create(
            call=make_call(),
            type=Record.END,
            timestamp='2016-02-29T12:00:00.0Z'
        )
    assert 'There is no start record for this call' in str(excinfo)


def test_invalid_end_record_timestamp(make_start_record):
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


def test_records_timestamps_cannot_be_equal(make_start_record):
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


def test_unique_timestamp_for_source(make_call_record):
    with pytest.raises(DRFValidationError) as excinfo:
        make_call_record(
            id='42',
            source='99988526423',
            destination='9933468278',
            start_timestamp='2017-12-12T04:57:13Z',
            end_timestamp='2017-12-12T06:10:56Z'
        )
        make_call_record(
            id='43',
            source='99988526423',
            destination='9933468278',
            start_timestamp='2017-12-12T04:57:13Z',
            end_timestamp='2017-12-12T06:10:56Z'
        )
    error_msg = ('There is already a start record for this source and '
                 'timestamp')
    assert error_msg in str(excinfo)


def test_unique_timestamp_for_destination(make_call_record):
    with pytest.raises(DRFValidationError) as excinfo:
        make_call_record(
            id='42',
            source='99988526456',
            destination='9933468278',
            start_timestamp='2017-12-12T04:57:13Z',
            end_timestamp='2017-12-12T06:10:56Z'
        )
        make_call_record(
            id='43',
            source='99988526423',
            destination='9933468278',
            start_timestamp='2017-12-12T04:57:13Z',
            end_timestamp='2017-12-12T06:10:56Z'
        )
    error_msg = ('There is already a start record for this destination '
                 'and timestamp')
    assert error_msg in str(excinfo)


def test_unique_start_record_for_source(make_start_record):
    with pytest.raises(DRFValidationError) as excinfo:
        make_start_record(
            id='42',
            source='99988526456',
            destination='9933468278',
            timestamp='2017-12-12T04:57:13Z',
        )
        make_start_record(
            id='43',
            source='99988526456',
            destination='1133468279',
            timestamp='2017-12-12T05:17:13Z',
        )
    error_msg = 'There is already an ongoing call from this source'
    assert error_msg in str(excinfo)


def test_unique_start_record_for_destination(make_start_record):
    with pytest.raises(DRFValidationError) as excinfo:
        make_start_record(
            id='42',
            source='99988526456',
            destination='9933468278',
            timestamp='2017-12-12T04:57:13Z',
        )
        make_start_record(
            id='43',
            source='99988526000',
            destination='9933468278',
            timestamp='2017-12-12T05:17:13Z',
        )
    error_msg = 'There is already an ongoing call for this destination'
    assert error_msg in str(excinfo)

def test_record_overlap_for_source(make_call_record, make_start_record):
    with pytest.raises(DRFValidationError) as excinfo:
        make_call_record(
            id='42',
            source='99988526000',
            destination='9933468278',
            start_timestamp='2017-12-12T04:57:13Z',
            end_timestamp='2017-12-12T06:10:56Z'
        )
        make_start_record(
            id='43',
            source='99988526000',
            destination='9933468278',
            timestamp='2017-12-12T05:17:13Z',
        )
    error_msg = ('There is already a call record for this source in this '
                 'interval.')
    assert error_msg in str(excinfo)

def test_record_overlap_for_destination(make_call_record, make_start_record):
    with pytest.raises(DRFValidationError) as excinfo:
        make_call_record(
            id='42',
            source='99988526000',
            destination='9933468278',
            start_timestamp='2017-12-12T04:57:13Z',
            end_timestamp='2017-12-12T06:10:56Z'
        )
        make_start_record(
            id='43',
            source='99988526022',
            destination='9933468278',
            timestamp='2017-12-12T05:17:13Z',
        )
    error_msg = ('There is already a call record for this destination in '
                 'this interval.')
    assert error_msg in str(excinfo)

def test_end_record_overlap_for_destination(make_call_record):
    with pytest.raises(DRFValidationError) as excinfo:
        make_call_record(
            id='42',
            source='99988526000',
            destination='9933468278',
            start_timestamp='2017-12-12T05:00:00Z',
            end_timestamp='2017-12-12T06:00:00Z'
        )
        make_call_record(
            id='43',
            source='99988526333',
            destination='9933468278',
            start_timestamp='2017-12-12T04:00:00Z',
            end_timestamp='2017-12-12T06:30:00Z'
        )
    error_msg = ('Cannot end this call overlapping another call record with '
                 'the same destination')
    assert error_msg in str(excinfo)

def test_end_record_overlap_for_source(make_call_record):
    with pytest.raises(DRFValidationError) as excinfo:
        make_call_record(
            id='42',
            source='99988526000',
            destination='9933468278',
            start_timestamp='2017-12-12T05:00:00Z',
            end_timestamp='2017-12-12T06:00:00Z'
        )
        make_call_record(
            id='43',
            source='99988526000',
            destination='9933468555',
            start_timestamp='2017-12-12T04:00:00Z',
            end_timestamp='2017-12-12T06:30:00Z'
        )
    error_msg = ('Cannot end this call overlapping another call record with '
                 'the same source')
    assert error_msg in str(excinfo)