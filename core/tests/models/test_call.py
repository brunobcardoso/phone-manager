import pytest
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from core.models import Call


def test_call_creation():
    call = Call.objects.create(
        id='42',
        source='99988526423',
        destination='9993468278')

    assert isinstance(call, Call)
    assert call.call_id == call.id
    assert call.__str__() == f'{call.id}'


def test_source_and_destination_cannot_be_equal(make_call):
    with pytest.raises(expected_exception=DRFValidationError) as excinfo:
        make_call(
            source='99988526423',
            destination='99988526423'
        )
    assert 'Source and Destination cannot be equal' in str(excinfo)


def test_invalid_phone_number_less_than_10_digits(make_call):
    with pytest.raises(ValidationError) as excinfo:
        make_call(
            source='99988526',
            destination='99988'
        )
    assert 'source' in str(excinfo)
    assert 'destination' in str(excinfo)
    assert 'Invalid phone number.' in str(excinfo)


def test_invalid_phone_number_more_than_11_digits(make_call):
    with pytest.raises(ValidationError) as excinfo:
        make_call(
            source='9998852600000',
            destination='999885264230000'
        )
    assert 'source' in str(excinfo)
    assert 'destination' in str(excinfo)
    assert 'Invalid phone number.' in str(excinfo)


def test_invalid_phone_number_format(make_call):
    with pytest.raises(ValidationError) as excinfo:
        make_call(
            source='darth vader',
            destination='luke skywalker'
        )
    assert 'source' in str(excinfo)
    assert 'destination' in str(excinfo)
    assert 'Invalid phone number.' in str(excinfo)
