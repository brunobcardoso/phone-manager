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


@pytest.mark.django_db
@pytest.fixture()
def make_call():
    def _make_call(id='42', source='99988526423', destination='9993468278'):
        call = models.Call.objects.create(
            id=id,
            source=source,
            destination=destination
        )
        return call

    return _make_call


@pytest.fixture()
def make_start_record(make_call):
    def _make_start_record(timestamp=timezone.now().isoformat()):
        call = make_call()
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
    def _make_call_record(start_timestamp=start, end_timestamp=end):
        call = make_call()
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
