from __future__ import absolute_import
import decimal
import trafaret as t


class Decimal(t.Trafaret):
    def transform(self, value, context=None):
        try:
            return decimal.Decimal(value)
        except (ValueError, TypeError, decimal.InvalidOperation):
            raise t.DataError('Not a number')
