from rest_framework import serializers

from core.models import Call, Record, Bill


class CallSerializer(serializers.ModelSerializer):
    call_id = serializers.IntegerField(required=True)
    source = serializers.CharField(
        required=True,
        validators=[Call.phone_validator]
    )
    destination = serializers.CharField(
        required=True,
        validators=[Call.phone_validator]
    )

    def validate(self, attrs):
        call_data = {
            'id': attrs.get('call_id'),
            'source': attrs.get('source'),
            'destination': attrs.get('destination')
        }

        call = Call(**call_data)
        call.validate_source_destination()
        call.full_clean()

        return attrs


class StartRecordSerializer(CallSerializer):
    class Meta:
        model = Record
        exclude = ('call',)

    def create(self, validated_data):
        call_data = {
            'id': validated_data.get('call_id'),
            'source': validated_data.get('source'),
            'destination': validated_data.get('destination')
        }

        Record.objects.validade_unique_source_timestamp(
            source=validated_data['source'],
            timestamp=validated_data['timestamp']
        )
        Record.objects.validade_unique_destination_timestamp(
            destination=validated_data['destination'],
            timestamp=validated_data['timestamp']
        )

        call = Call.objects.create(**call_data)

        record_data = {
            'call': call,
            'type': validated_data.get('type'),
            'timestamp': validated_data.get('timestamp')
        }

        Record.objects.create(**record_data)

        return validated_data


class EndRecordSerializer(serializers.ModelSerializer):
    call_id = serializers.IntegerField(required=True)

    class Meta:
        model = Record
        exclude = ('call',)

    def validate(self, attrs):
        record = Record(**attrs)
        record.full_clean()

        return attrs

    def create(self, validated_data):
        call = Call.objects.get(id=validated_data.get('call_id'))

        record_data = {
            'call': call,
            'type': validated_data.get('type'),
            'timestamp': validated_data.get('timestamp')
        }

        Record.objects.create(**record_data)

        return validated_data


class BillSerializer(serializers.ModelSerializer):
    destination = serializers.SerializerMethodField()
    call_start_date = serializers.SerializerMethodField()
    call_start_time = serializers.SerializerMethodField()
    call_duration = serializers.SerializerMethodField()
    call_price = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = ('destination', 'call_start_date', 'call_start_time',
                  'call_duration', 'call_price')

    def get_destination(self, obj):
        return obj.call.destination

    def get_call_start_date(self, obj):
        return obj.start.date()

    def get_call_start_time(self, obj):
        return obj.start.time()

    def get_call_duration(self, obj):
        return obj.duration

    def get_call_price(self, obj):
        price = f'R$ {obj.price:.2f}'.replace('.', ',')
        return price
