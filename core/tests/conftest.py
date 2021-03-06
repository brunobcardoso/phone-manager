import os

import django
import pytest
from django.conf import settings
from django.utils import timezone

from core import models

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonemanager.config.settings')


def pytest_configure():
    settings.DEBUG = False
    django.setup()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.mark.django_db
@pytest.fixture()
def make_call():
    def _make_call(id='42', source='99988526423', destination='9933468278'):
        call = models.Call.objects.create(
            id=id,
            source=source,
            destination=destination
        )
        return call

    return _make_call


@pytest.fixture()
def make_start_record(make_call):
    start = timezone.now().isoformat()

    def _make_start_record(timestamp=start, id='42', source='99988526423',
                           destination='9933468278'):
        call = make_call(id=id, source=source, destination=destination)
        start_record = models.Record.objects.create(
            call=call,
            type=models.Record.START,
            timestamp=timestamp
        )
        return start_record

    return _make_start_record


@pytest.fixture()
def make_call_record(make_call):
    start = timezone.now().isoformat()
    end = (timezone.now() + timezone.timedelta(minutes=5)).isoformat()

    settings.STD_HOUR_START = 6
    settings.STD_HOUR_END = 22
    settings.STD_STANDING_CHARGE = 0.36
    settings.RDC_STANDING_CHARGE = 0.36
    settings.STD_MINUTE_CHARGE = 0.09

    def _make_call_record(start_timestamp=start, end_timestamp=end, id='42',
                          source='99988526423', destination='9933468278'):
        call = make_call(id=id, source=source, destination=destination)
        models.Record.objects.create(
            call=call,
            type=models.Record.START,
            timestamp=start_timestamp
        )
        models.Record.objects.create(
            call=call,
            type=models.Record.END,
            timestamp=end_timestamp
        )
        return call

    return _make_call_record
