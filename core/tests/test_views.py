import pytest
from django.utils import timezone

from core.models import Call, Record


@pytest.mark.django_db
class TestRecordsAPI:

    @pytest.fixture()
    def call_record(self):
        call = Call.objects.create(
            id='42',
            source='99988526423',
            destination='9993468278'
        )
        Record.objects.create(
            call=call,
            type=Record.START,
            timestamp='2018-09-25T08:20:00Z'
        )

    def test_create_start_record_success(self, client):
        data = {
            'type': Record.START,
            'call_id': 42,
            'timestamp': '2018-09-25T08:28:00Z',
            'source': '11987665433',
            'destination': '11928736537'
        }
        response = client.post('/records', data)
        assert response.status_code == 201
        assert Record.objects.count() == 1
        assert response.json() == data

    def test_create_end_record_success(self, client, call_record):
        data = {
            'type': Record.END,
            'call_id': 42,
            'timestamp': '2018-09-25T08:28:00Z',
        }
        response = client.post('/records', data)
        assert response.status_code == 201
        assert Record.objects.filter(type=Record.END).count() == 1
        assert response.json() == data

    def test_create_record_fails(self, client):
        response = client.post('/records')
        assert response.status_code == 400
