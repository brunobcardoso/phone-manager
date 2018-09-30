import coreapi
import coreschema
from rest_framework import schemas


def get_record_schema():
    """
    Generates a ManualSchema for RecordCreate view
    """
    record_schema = schemas.ManualSchema(
        fields=[
            coreapi.Field(
                "call_id",
                required=True,
                location="form",
                schema=coreschema.String(
                    description='Unique for each call record pair'
                ),
            ),
            coreapi.Field(
                "type",
                required=True,
                location="form",
                schema=coreschema.String(
                    description='Indicate if it\'s a call start or end record'
                )
            ),
            coreapi.Field(
                "timestamp",
                required=True,
                location="form",
                schema=coreschema.String(
                    description='The timestamp of when the event occurred'
                )
            ),
            coreapi.Field(
                "source",
                required=False,
                location="form",
                schema=coreschema.String(
                    description='The subscriber phone number that originated '
                                'the call'
                )
            ),
            coreapi.Field(
                "destination",
                required=False,
                location="form",
                schema=coreschema.String(
                    description='The phone number receiving the call'
                )
            ),
        ],
        encoding="application/json",
    )

    return record_schema


def get_bill_schema():
    """
    Generates a ManualSchema for BillList view
    """
    bill_schema = schemas.ManualSchema(fields=[
        coreapi.Field(
            "subscriber",
            required=True,
            location="path",
            schema=coreschema.String(
                description='Subscriber telephone number'
            )
        ),
        coreapi.Field(
            "reference",
            required=False,
            location="query",
            schema=coreschema.String(
                description='The reference period (month/year) '
            )
        )
    ])

    return bill_schema
