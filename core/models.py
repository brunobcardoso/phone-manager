from datetime import timedelta, time
from decimal import Decimal

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError


class Call(models.Model):
    """
    Stores a call entry
    """
    phone_validator = RegexValidator(
        regex=r'^(([1-9]{2})(?:[2-8]|9[1-9])[0-9]{7})$',
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
            raise ValidationError('Source and Destination cannot be equal')

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

    def last_source_record_type(self, call):
        """
        Returns the last record type for a source
        """
        return self.filter(
            call__source=call.source
        ).values_list('type', flat=True).last()

    def last_destination_record_type(self, call):
        """
        Returns the last record type for a destination
        """
        return self.filter(
            call__destination=call.destination
        ).values_list('type', flat=True).last()

    def type_less_than(self, call, timestamp, phone):
        """
        Returns the first type of a record less than a given timestamp
        """
        if phone == 'source':
            return self.filter(
                call__source=call.source,
                timestamp__lt=timestamp
            ).order_by('timestamp').values_list('type', flat=True).last()
        else:
            return self.filter(
                call__destination=call.destination,
                timestamp__lt=timestamp
            ).order_by('timestamp').values_list('type', flat=True).last()

    def type_greater_than(self, call, timestamp, phone):
        """
        Returns the first type of a record greater than a given timestamp
        """
        if phone == 'source':
            return self.filter(
                call__source=call.source,
                timestamp__gte=timestamp
            ).order_by('timestamp').values_list('type', flat=True).first()
        else:
            return self.filter(
                call__destination=call.destination,
                timestamp__gte=timestamp
            ).order_by('timestamp').values_list('type', flat=True).first()


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
                raise ValidationError('There is no start record for this call')

    def validate_timestamp_end_record(self):
        """
        Checks if end record timestamp is valid (Greater than start record)
        """
        if self.type == Record.END:
            start_record = Record.objects.get(
                call=self.call,
                type=Record.START)
            if self.timestamp <= start_record.timestamp:
                raise ValidationError('Timestamp of end record cannot be less '
                                      'or equal to start record')

    def validate_unique_source_timestamp(self):
        """
        Checks if exists a call record for the same source and timestamp
        """
        conflict = Record.objects.filter(
            call__source=self.call.source,
            timestamp=self.timestamp).exists()
        if conflict:
            raise ValidationError('There is already a start record for this '
                                  'source and timestamp')

    def validate_unique_destination_timestamp(self):
        """
        Checks if exists a call record for the same destination and timestamp
        """
        conflict = Record.objects.filter(
            call__destination=self.call.destination,
            timestamp=self.timestamp).exists()
        if conflict:
            raise ValidationError('There is already a start record for this '
                                  'destination and timestamp')

    def validate_unique_start_record_for_source(self):
        """
        Checks if exists a ongoing call for the same source
        """
        if self.type == Record.START:
            last_type = Record.objects.last_source_record_type(call=self.call)
            if last_type == Record.START:
                raise ValidationError('There is already an ongoing call from '
                                      'this source')

    def validate_unique_start_record_for_destination(self):
        """
        Checks if exists a ongoing call for the same destination
        """
        if self.type == Record.START:
            last_type = Record.objects.last_destination_record_type(
                call=self.call
            )
            if last_type == Record.START:
                raise ValidationError('There is already an ongoing call for '
                                      'this destination')

    def validate_overlapping_record_for_source(self):
        """
        Checks if a call does not overlap an existent record
        """
        type_less_than = Record.objects.type_less_than(
            call=self.call,
            timestamp=self.timestamp,
            phone='source'
        )
        type_greater_than = Record.objects.type_greater_than(
            call=self.call,
            timestamp=self.timestamp,
            phone='source'
        )
        if type_less_than == Record.START and type_greater_than == Record.END:
            raise ValidationError('There is already a call record for this '
                                  'source in this interval.')
        elif type_less_than == Record.END and self.type == Record.END:
                raise ValidationError('Cannot end this call overlapping '
                                      'another call record with the same '
                                      'source')

    def validate_overlapping_record_for_destination(self):
        """
        Checks if a call does not overlap an existent range of dates
        """
        type_less_than = Record.objects.type_less_than(
            call=self.call,
            timestamp=self.timestamp,
            phone='destination'
        )
        type_greater_than = Record.objects.type_greater_than(
            call=self.call,
            timestamp=self.timestamp,
            phone='destination'
        )
        if type_less_than == Record.START and type_greater_than == Record.END:
            raise ValidationError('There is already a call record for this '
                                  'destination in this interval.')
        elif type_less_than == Record.END and self.type == Record.END:
                raise ValidationError('Cannot end this call overlapping '
                                      'another call record with the same '
                                      'destination')


    def save(self, *args, **kwargs):
        self.clean_fields()
        self.validate_exists_start_record_before_end_record()
        self.validate_timestamp_end_record()
        self.validate_unique_source_timestamp()
        self.validate_unique_destination_timestamp()
        self.validate_unique_start_record_for_source()
        self.validate_unique_start_record_for_destination()
        self.validate_overlapping_record_for_source()
        self.validate_overlapping_record_for_destination()
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
