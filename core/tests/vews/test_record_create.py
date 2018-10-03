from core.models import Record


def test_create_start_record_success(client):
    data = {
        'type': Record.START,
        'call_id': 42,
        'timestamp': '2018-09-25T08:28:00Z',
        'source': '11987665433',
        'destination': '9933468278'
    }
    response = client.post('/records', data)
    assert response.status_code == 201
    assert Record.objects.count() == 1
    assert response.json() == data


def test_create_end_record_success(client, make_start_record):
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


def test_create_record_fails(client):
    response = client.post('/records')
    assert response.status_code == 400
