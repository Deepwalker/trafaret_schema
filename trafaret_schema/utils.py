import re
import sre_constants
import trafaret as t


def then(trafaret_creator):
    """
    Its just fun then to write `& then(just())` :D
    """
    def inner(value):
        return trafaret_creator(value)
    return inner


def just(trafaret):
    """Returns trafaret and ignoring values"""
    def create(value):
        return trafaret
    return create


class All(t.Trafaret):
    def __init__(self, trafarets):
        self.trafarets = [t.ensure_trafaret(trafaret) for trafaret in trafarets]

    def transform(self, value, context=None):
        errors = []
        for trafaret in self.trafarets:
            res = t.catch_error(trafaret, value, context=context)
            if isinstance(res, t.DataError):
                errors.append(res)
        if errors:
            raise t.DataError(errors)
        return value

    def __repr__(self):
        return '<All trafarets=[%s]>' % ', '.join(repr(r) for r in self.trafarets)


class Any(t.Trafaret):
    def __init__(self, trafarets):
        self.trafarets = [t.ensure_trafaret(trafaret) for trafaret in trafarets]

    def transform(self, value, context=None):
        errors = []
        for trafaret in self.trafarets:
            res = t.catch_error(trafaret, value, context=context)
            if isinstance(res, t.DataError):
                errors.append(res)
            else:
                return value
        raise t.DataError(errors)

    def __repr__(self):
        return '<Any trafarets=[%s]>' % ', '.join(repr(r) for r in self.trafarets)


class Not(t.Trafaret):
    def __init__(self, trafaret):
        self.trafaret = trafaret

    def transform(self, value, context=None):
        res = t.catch_error(self.trafaret, value, context=context)
        if not isinstance(res, t.DataError):
            raise t.DataError('Value must not be validated')
        return value


class Pattern(t.Trafaret):
    def check_and_return(self, value):
        try:
            re.compile(value)
            return value
        except sre_constants.error as e:
            raise t.DataError('Pattern is invalid due ' + str(e))


def all_strings_unique(strings):
    if len(strings) == len(set(strings)):
        return strings
    raise t.DataError('all strings must be unique')


unique_strings_list = t.List(t.String) >> all_strings_unique


def ensure_list(typ):
    return t.List(typ) | typ & (lambda x: [x])
