# Generated by Django 2.1.1 on 2018-10-03 05:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20180927_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='destination',
            field=models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(message='Invalid phone number. Valid format is composed of 10 or 11 digits. ie: AAXXXXXXXXX, where AA is the area code and XXXXXXXXX is the phone number', regex='^(([1-9]{2})(?:[2-8]|9[1-9])[0-9]{7})$')]),
        ),
        migrations.AlterField(
            model_name='call',
            name='source',
            field=models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(message='Invalid phone number. Valid format is composed of 10 or 11 digits. ie: AAXXXXXXXXX, where AA is the area code and XXXXXXXXX is the phone number', regex='^(([1-9]{2})(?:[2-8]|9[1-9])[0-9]{7})$')]),
        ),
    ]
