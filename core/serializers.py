from rest_framework import serializers

from core.models import Call, Record


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
