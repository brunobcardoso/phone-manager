import pytest

from core.models import Record


@pytest.mark.django_db
class TestRecordsAPI:
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

    def test_create_end_record_success(self, client, make_start_record):
        make_start_record('2018-09-25T08:20:00Z')
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


@pytest.mark.django_db
class TestBillsApi:
    def test_get_bill_call_record_success(self, client, make_call_record):
        make_call_record()
        subscriber = '99988526423'
        response = client.get(f'/bills/{subscriber}')
        assert response.status_code == 200
        assert subscriber == response.data['subscriber']

    def test_get_bill_valid_reference_period(self, client, make_call_record):
        make_call_record(
            start_timestamp='2018-08-25T08:28:00Z',
            end_timestamp='2018-08-25T08:30:00Z'
        )
        subscriber = '99988526423'
        reference = '08/2018'
        response = client.get(f'/bills/{subscriber}?reference={reference}')
        assert response.status_code == 200

    def test_invalid_reference_period_date(self, client, make_call_record):
        subscriber = '99988526423'
        reference = '08/2098'
        response = client.get(f'/bills/{subscriber}?reference={reference}')
        error_msg = (b'["Invalid reference period. It\'s only possible to get '
                     b'a telephone bill after the reference period has '
                     b'ended."]')
        assert response.status_code == 400
        assert error_msg == response.content

    def test_invalid_reference_period_format(self, client, make_call_record):
        subscriber = '99988526423'
        reference = '082018'
        response = client.get(f'/bills/{subscriber}?reference={reference}')
        error_msg = (b'{"detail":"Invalid reference period format. Try one of '
                     b'the following: MM/YYYY, MM-YYYY, MM:YYYY, MM.YYYY '
                     b'where MM is the month and YYYY is the year."}')
        assert response.status_code == 400
        assert error_msg == response.content
