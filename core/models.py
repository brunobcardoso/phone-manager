from datetime import timedelta, datetime, time
from decimal import Decimal

from django.conf import settings
from django.core.validators import RegexValidator, ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Call(models.Model):
    """
    Stores a call entry
    """
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
        """
        Checks if a start call record exists
        """
        return self.filter(call=call, type=Record.START).exists()

    def timestamp(self, type, call_id):
        """
        Returns a timestamp of a call record associated with call_id and type
        criteria
        """
        timestamp = self.get(call__id=call_id, type=type).timestamp
        return timestamp


class Record(models.Model):
    """
    Stores start and end records entry, related to :model:`core.Call`
    """
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

    def validate_timestamp_end_record(self):
        if self.type == Record.END:
            start_record = Record.objects.get(
                call=self.call,
                type=Record.START)
            if self.timestamp <= start_record.timestamp:
                raise ValidationError(
                    message='Timestamp of end record cannot be less or equal '
                            'to start record'
                )

    def save(self, *args, **kwargs):
        self.clean_fields()
        self.validate_exists_start_record_before_end_record()
        self.validate_timestamp_end_record()
        super(Record, self).save(*args, **kwargs)


class BillQueryset(models.QuerySet):
    def get_bills(self, source, m, y):
        """
        Returns a queryset with selected bills based on source number and
        reference period. m(month) and y(year)
        """
        return self.filter(call__source=source, end__year=y,
                           end__month=m).all()


class Bill(models.Model):
    """
    Stores a bill call record entry, related to :model:`core.Call` and
    :model:`core.Record`
    """
    call = models.OneToOneField(Call, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    objects = BillQueryset.as_manager()

    @property
    def duration(self):
        total_sec = int((self.end - self.start).total_seconds())
        hours, rem = divmod(total_sec, 60 * 60)
        minutes, seconds = divmod(rem, 60)
        return f'{hours}h{minutes}m{seconds}s'

    @property
    def total_minutes(self):
        minutes, _ = divmod((self.end - self.start).total_seconds(), 60)
        return int(minutes)

    def standard_minutes(self):
        record_start = self.start.replace(second=0, microsecond=0)
        t_minutes = self.total_minutes

        std_start = time(hour=settings.STD_HOUR_START)
        std_end = time(hour=settings.STD_HOUR_END)

        minutes = 0
        for minute in range(t_minutes):
            cond_1 = std_start <= record_start.time() < std_end
            # excluding end_limit
            cond_2 = (record_start + timedelta(minutes=1)).time() < std_end
            if all([cond_1, cond_2]):
                minutes += 1
            record_start += timedelta(minutes=1)
        return minutes

    def __str__(self):
        return f'call_id: {self.call} - price: {self.price}'

    def standing_charge(self):
        record_start = self.start
        std_start_hour = settings.STD_HOUR_START
        std_end_hour = settings.STD_HOUR_END

        if std_start_hour <= record_start.hour < std_end_hour:
            st_charge = settings.STD_STANDING_CHARGE
        else:
            st_charge = settings.RDC_STANDING_CHARGE
        return st_charge

    def calculate_price(self):
        standard_minutes = self.standard_minutes()
        reduced_minutes = self.total_minutes - standard_minutes

        std_minute_charge = settings.STD_MINUTE_CHARGE
        rdc_minute_charge = settings.RDC_MINUTE_CHARGE
        std_price = (Decimal(standard_minutes) * Decimal(std_minute_charge))
        rdc_price = Decimal(reduced_minutes) * Decimal(rdc_minute_charge)

        standing_charge = self.standing_charge()

        total = std_price + rdc_price + Decimal(standing_charge)
        return total.quantize(Decimal('0.01'))

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
        self.price = self.calculate_price()
        super(Bill, self).save(*args, **kwargs)


@receiver(post_save, sender=Record)
def create_bill(sender, instance, created, **kwargs):
    """
    On post save of a end call record, a bill created
    """
    if created and instance.type == Record.END:
        call = Call.objects.get(id=instance.call_id)
        Bill.objects.create(call=call)
