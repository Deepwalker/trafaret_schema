import time
import trafaret as t
from .utils import just


def parse_date():
    @t.Call
    def check_datetime(value):
        import arrow
        try:
            return arrow.get(value).naive
        except arrow.parser.ParserError:
            return t.DataError('value is not in proper date/time format')
    return check_datetime


@t.Call
def parse_time(value):
    try:
        return time.strptime(value, '%H:%M')
    except ValueError:
        raise t.DataError('Not a valid time')


# Because phone numbers have not any proper format at all
check_phone = t.OnError(t.Regexp('.+'), 'Bad formatted phone number')


def check_from_register(format_name, context=None):
    register = context.get_register()
    custom_format = register.get_format(format_name)
    if not custom_format:
        raise t.DataError('Register does not contains this format', value=format_name)
    return custom_format


format_trafaret = t.OnError(
    t.Or(
        t.Call(check_from_register),
        t.Atom('date-time') & just(parse_date()),
        t.Atom('date') & just(parse_date()),
        t.Atom('time') & just(parse_time),
        t.Atom('email') & just(t.Email),
        t.Atom('phone') & just(check_phone),
        t.Atom('uri') & just(t.URL),
        t.Atom('ipv4') & just(t.IPv4),
        t.Atom('ipv6') & just(t.IPv6),
    ),
    'Format is not defined and unsupported by this implementation',
)

# TODO
# 'hostname',
# 'uri-reference',
# 'uri-template',
# 'json-pointer',
