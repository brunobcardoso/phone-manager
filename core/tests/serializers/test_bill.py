from core.models import Bill
from core.serializers import BillSerializer


def test_bill_data(make_call_record):
    call_record = make_call_record()

    queryset = Bill.objects.filter(call__source=call_record.source)
    serializer = BillSerializer(queryset, many=True)

    data = serializer.data[0]
    assert data.__len__() == 5
    assert data['destination'] == '9933468278'
