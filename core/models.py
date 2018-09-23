from django.db import models
from django.core.validators import RegexValidator


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
        return f'{self.id}, {self.source}, {self.destination}'

    class Meta:
        verbose_name = 'call'
        verbose_name_plural = 'calls'
