from django.core.validators import RegexValidator
from django.db import models


class Call(models.Model):
    phone_validator = RegexValidator(
        regex=r'^((?:[1-9]{2})(?:[2-8]|9[1-9])[0-9]{7})$',
        message='Invalid format. Valid format is composed of 10 or 11 digits.')

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


class Record(models.Model):
    START, END = ('start', 'end')
    CALL_TYPES = (
        (START, 'Start'),
        (END, 'End')
    )

    call = models.ForeignKey(Call, related_name='records', on_delete=models.CASCADE)
    type = models.CharField(max_length=5, choices=CALL_TYPES, default=START)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f'{self.call}, {self.type}, {self.timestamp}'

    @property
    def start_call_exists(self):
        return Record.objects.filter(call=self.call).exists()

    class Meta:
        unique_together = ("call", "type")
        verbose_name = 'record'
        verbose_name_plural = 'records'
