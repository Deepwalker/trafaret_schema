import decimal

import pytest
import trafaret_schema


def test_number():
    reg = trafaret_schema.Register()
    schema = trafaret_schema.json_schema(
        {
            "type": "number",
        },
        reg,
    )
    assert schema('100.0') == '100.0'
    assert schema(decimal.Decimal('100.0')) == decimal.Decimal('100.0')


def test_number_as_decimal():
    reg = trafaret_schema.Register()
    reg.reg_format("decimal", decimal.Decimal)
    schema = trafaret_schema.json_schema(
        {
            "type": "number",
            "format": "decimal",
        },
        reg,
    )
    assert schema('100.0') == decimal.Decimal('100.0')
