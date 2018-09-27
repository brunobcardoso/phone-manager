from django.core.validators import RegexValidator, ValidationError
from django.db import models


class Call(models.Model):
    phone_validator = RegexValidator(
        regex=r'(^[1-9]{2})([1-9]\d{7,8}$)',
        message='Invalid phone number. Valid format is composed of 10 or 11 '
                'digits. ie: AAXXXXXXXXX, where AA is the area code and '
                'XXXXXXXXX is the phone number')

    id = models.PositiveIntegerField(primary_key=True)
    source = models.CharField(max_length=11, validators=[phone_validator])
    destination = models.CharField(max_length=11, validators=[phone_validator])

    @property
    def call_id(self):
        return self.id

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'call'
        verbose_name_plural = 'calls'

    def validate_source_destination(self):
        if self.source == self.destination:
            raise ValidationError(
                message='Source and Destination cannot be equal'
            )

    def save(self, *args, **kwargs):
        self.clean_fields()
        self.validate_source_destination()
        super(Call, self).save(*args, **kwargs)


class RecordManager(models.Manager):
    def start_call_exists(self, call):
        return self.filter(call=call, type=Record.START).exists()

    def timestamp(self, type, call_id):
        timestamp = self.get(call__id=call_id, type=type).timestamp
        return timestamp


class Record(models.Model):
    START, END = ('start', 'end')
    CALL_TYPES = (
        (START, 'Start'),
        (END, 'End')
    )

    call = models.ForeignKey(
        Call,
        related_name='records',
        on_delete=models.CASCADE
    )

    type = models.CharField(
        max_length=5,
        choices=CALL_TYPES,
        default=START
    )

    timestamp = models.DateTimeField()

    objects = RecordManager()

    def __str__(self):
        return f'{self.call}, {self.type}, {self.timestamp}'

    class Meta:
        unique_together = ("call", "type")
        verbose_name = 'record'
        verbose_name_plural = 'records'

    def validate_exists_start_record_before_end_record(self):
        if self.type == Record.END:
            if not Record.objects.start_call_exists(self.call):
                raise ValidationError(
                    message='There is no start record for this call'
                )

    def validate_timestamp_end_record_after_timestamp_start_record(self):
        if self.type == Record.END:
            start_record = Record.objects.get(
                call=self.call,
                type=Record.START)
            if self.timestamp < start_record.timestamp:
                raise ValidationError(
                    message='Timestamp of end record cannot be less than '
                            'start record'
                )

    def save(self, *args, **kwargs):
        self.clean_fields()
        self.validate_exists_start_record_before_end_record()
        self.validate_timestamp_end_record_after_timestamp_start_record()
        super(Record, self).save(*args, **kwargs)


class Bill(models.Model):
    call = models.OneToOneField(Call, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return f'call_id: {self.call} - price: {self.price}'

    class Meta:
        verbose_name = 'bill'
        verbose_name_plural = 'bills'

    def save(self, *args, **kwargs):
        self.start = Record.objects.timestamp(
            call_id=self.call.id,
            type=Record.START
        )
        self.end = Record.objects.timestamp(
            call_id=self.call.id,
            type=Record.END
        )
        super(Bill, self).save(*args, **kwargs)
