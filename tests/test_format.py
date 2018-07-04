import datetime
import unittest

import pytest
import trafaret as t
import trafaret_schema
from trafaret_schema.format import (
    parse_date,
    parse_time,
)


def test_parse_date():
    check = parse_date()

    assert check('2012-01-01') == datetime.datetime(2012, 1, 1)

    with pytest.raises(t.DataError):
        check('not a date')


def test_parse_time():
    parsed = parse_time('11:59')
    assert parsed.tm_hour == 11
    assert parsed.tm_min == 59

    with pytest.raises(t.DataError):
        parse_time('not a date')


class TestFormats(unittest.TestCase):
    def test_email(self):
        schema = trafaret_schema.json_schema({
            "type": "object",
            "properties": {
                "email": {"format": "email"}
            },
        })
        schema({'email': 'norfolk@inductries.co'})

    def test_ipv4(self):
        schema = trafaret_schema.json_schema({
            "type": "object",
            "properties": {
                "ip": {"format": "ipv4"}
            },
        })
        schema({'ip': '127.0.0.1'})

    def test_ipv6(self):
        schema = trafaret_schema.json_schema({
            "type": "object",
            "properties": {
                "ip": {"format": "ipv6"}
            },
        })
        schema({'ip': '::1'})

    def test_datetime(self):
        schema = trafaret_schema.json_schema({
            "type": "object",
            "properties": {
                "datetime": {"format": "date-time"}
            },
        })
        schema({'datetime': '2017-09-02T00:00:00.59Z'})
        schema({'datetime': '2017-09-02T00:00:00.59+02:00'})

    def test_date(self):
        schema = trafaret_schema.json_schema({
            "type": "object",
            "properties": {
                "datetime": {"format": "date"}
            },
        })
        schema({'datetime': '2017-09-02'})

    def test_phone(self):
        schema = trafaret_schema.json_schema({
            "type": "object",
            "properties": {
                "phone": {"format": "phone"}
            },
        })
        schema({'phone': '+7 927 728 67 67'})

    def test_time(self):
        schema = trafaret_schema.json_schema({
            "type": "object",
            "properties": {
                "time": {"format": "time"}
            },
        })
        schema({'time': '19:59'})

    def test_reg_format(self):
        register = trafaret_schema.Register()
        register.reg_format('any_ip', t.IP)

        schema = trafaret_schema.json_schema({
                "type": "object",
                "properties": {
                    "ip_addr": {"format": "any_ip"}
                },
            },
            context=register,
        )
        schema({'ip_addr': '192.168.0.1'})
        schema({'ip_addr': '::1'})
