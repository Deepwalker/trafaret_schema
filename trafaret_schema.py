import re
import sre_constants
import trafaret as t


# Utils
#######
def then(trafaret_creator):
    def check_schema_value(value):
        return trafaret_creator(value)
    return check_schema_value

def just(trafaret):
    def create(value):
        return trafaret
    return create


class All(t.Trafaret):
    def __init__(self, trafarets):
        self.trafarets = trafarets

    def check_and_return(self, value):
        errors = []
        for trafaret in self.trafarets:
            res = t.catch_error(trafaret, value)
            if isinstance(res, t.DataError):
                errors.append(res)
        if errors:
            raise t.DataError(errors)
        return value

    def __repr__(self):
        return '<All trafarets=[%s]>' % ', '.join(repr(r) for r in self.trafarets)


class Any(t.Trafaret):
    def __init__(self, trafarets):
        self.trafarets = trafarets

    def check_and_return(self, value):
        errors = []
        for trafaret in self.trafarets:
            res = t.catch_error(trafaret, value)
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

    def check_and_return(self, value):
        res = t.catch_error(self.trafaret, value)
        if not isinstance(res, t.DataError):
            raise t.DataError('Value must not be validated')
        return value


class Pattern(t.Trafaret):
    def check_and_return(self, value):
        try:
            re.compile(value)
            return value
        except sre_constants.error as e:
            raise t.DataError('Pattern is invalid due ' + e.msg)

def all_strings_unique(strings):
    if len(strings) == len(set(strings)):
        return strings
    return t.DataError('all strings must be unique')

unique_strings_list = t.List(t.String) >> all_strings_unique

ensure_list = lambda typ: t.List(typ) | typ & (lambda x: [x])


# JSON Schema implementation
############################
json_schema = t.Forward()

#json_schema_type = t.Enum('null', 'boolean', 'object', 'array', 'number', 'integer', 'string')
json_schema_type = (
    t.Atom('null') & then(just(t.Null()))
    | t.Atom('boolean') & then(just(t.Bool()))
    | t.Atom('object') & then(just(t.Type(dict)))
    | t.Atom('array') & then(just(t.Type(list)))
    | t.Atom('number') & then(just(t.Float()))
    | t.Atom('integer') & then(just(t.Int()))
    | t.Atom('string') & then(just(t.String()))
)

def multipleOf(multiplier):
    def check(value):
        if value % multiplier != 0:
            return t.DataError('%s is not devisible by %s' % (value, multiplier))
        return value
    return check

keywords = (
    t.Key('enum', optional=True, trafaret=t.List(t.Any) & then(lambda consts: t.Or(*(t.Atom(cnst) for cnst in consts)))), # uniq?
    t.Key('const', optional=True, trafaret=t.Any() & then(t.Atom)),
    t.Key('type', optional=True, trafaret=ensure_list(json_schema_type) & then(Any)),

    # predicates
    t.Key('allOf', optional=True, trafaret=t.List(json_schema) & then(All)),
    t.Key('anyOf', optional=True, trafaret=t.List(json_schema) & then(Any)),
    t.Key('oneOf', optional=True, trafaret=t.List(json_schema) & then(Any)),
    t.Key('not', optional=True, trafaret=json_schema & then(Not)),

    # number validation
    t.Key('multipleOf', optional=True, trafaret=t.Float(gt=0) & then(multipleOf)),
    t.Key('maximum', optional=True, trafaret=t.Float() & then(lambda maximum: t.Float(lte=maximum))),
    t.Key('exclusiveMaximum', optional=True, trafaret=t.Float() & then(lambda maximum: t.Float(lt=maximum))),
    t.Key('minimum', optional=True, trafaret=t.Float() & then(lambda minimum: t.Float(gte=minimum))),
    t.Key('exclusiveMinimum', optional=True, trafaret=t.Float() & then(lambda minimum: t.Float(gt=minimum))),

    # string
    t.Key('maxLength', optional=True, trafaret=t.Int(gte=0) & then(lambda length: t.String(max_length=length))),
    t.Key('minLength', optional=True, trafaret=t.Int(gte=0) & then(lambda length: t.String(min_length=length))),
    t.Key('pattern', optional=True, trafaret=Pattern() & then(lambda pattern: t.Regexp(pattern))),

    # array
    t.Key('items', optional=True, trafaret=ensure_list(json_schema)),
    t.Key('additionalItems', optional=True, trafaret=json_schema),
    t.Key('maxItems', optional=True, trafaret=t.Int(gte=0)),
    t.Key('minItems', optional=True, trafaret=t.Int(gte=0)),
    t.Key('uniqueItems', optional=True, trafaret=t.Bool()),
    t.Key('contains', optional=True, trafaret=json_schema),

    # object
    t.Key('maxProperties', optional=True, trafaret=t.Int(gte=0)),
    t.Key('minProperties', optional=True, trafaret=t.Int(gte=0)),
    t.Key('required', optional=True, trafaret=unique_strings_list),
    t.Key('properties', optional=True, trafaret=t.Mapping(t.String, json_schema)),
    t.Key('patternProperties', optional=True, trafaret=t.Mapping(Pattern, json_schema)),
    t.Key('additionalProperties', optional=True, trafaret=json_schema),
    t.Key('dependencies', optional=True, trafaret=t.Mapping(t.String, unique_strings_list | json_schema)),
    t.Key('propertyNames', optional=True, trafaret=json_schema),

    t.Key('format', optional=True, trafaret=t.Enum('date-time', 'date', 'time', 'email', 'phone', 'hostname', 'ipv4', 'ipv6', 'uri', 'uri-reference', 'uri-template', 'json-pointer')),
)

metadata = (
    t.Key('$id', optional=True, trafaret=t.URL),
    t.Key('$schema', optional=True, trafaret=t.URL),
    t.Key('$ref', optional=True, trafaret=t.String),
    t.Key('title', optional=True, trafaret=t.String),
    t.Key('description', optional=True, trafaret=t.String),
    t.Key('definitions', optional=True, trafaret=t.Mapping(t.String, json_schema)),
    t.Key('examples', optional=True, trafaret=t.List(t.Any)),
)

ignore_keys = {'$id', '$schema', '$ref', 'title', 'description', 'definitions', 'examples'}

def validate_schema(schema):
    touched_names = set()
    errors = {}
    keywords_checks = []
    for key in keywords:
        for k, v, names in key(schema):
            if isinstance(v, t.DataError):
                errors[k] = v
            else:
                keywords_checks.append(v)
            touched_names = touched_names.union(names)
    touched_names = touched_names.union(ignore_keys)
    schema_keys = set(schema.keys())
    for key in schema_keys - touched_names:
        errors[key] = '%s is not allowed key' % key
    if errors:
        raise t.DataError(errors)
    return All(keywords_checks)
json_schema << (t.Type(dict) & t.Call(validate_schema))
