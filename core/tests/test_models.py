import pytest

from core.models import Call


@pytest.mark.django_db
class TestCall:
    def create_call(self, id='42', source='99988526423', destination='9993468278'):
        return Call.objects.create(id=id, source=source, destination=destination)

    def test_call_creation(self):
        call = self.create_call()
        assert isinstance(call, Call)
        assert call.call_id == call.id
        assert call.__str__() == f'id: {call.id} - source: {call.source} - destination: {call.destination}'
