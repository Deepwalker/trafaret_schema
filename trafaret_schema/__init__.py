import re
import sre_constants
import trafaret as t


# Utils
#######
def then(trafaret_creator):
    return trafaret_creator


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
class Register:
    pass

json_schema_type = (
    t.Atom('null') & just(t.Null())
    | t.Atom('boolean') & just(t.Bool())
    | t.Atom('object') & just(t.Type(dict))
    | t.Atom('array') & just(t.Type(list))
    | t.Atom('number') & just(t.Float())
    | t.Atom('integer') & just(t.Int())
    | t.Atom('string') & just(t.String())
)


def multipleOf(multiplier):
    def check(value):
        if value % multiplier != 0:
            return t.DataError('%s is not devisible by %s' % (value, multiplier))
        return value
    return check


def uniq(lst):
    if len(set(lst)) < len(lst):
        return t.DataError('Array elements are not uniq')
    return lst


def required(names):
    def check(value):
        errors = {}
        for name in names:
            if name not in value:
                errors[name] = t.DataError('%s is required' % name)
        if errors:
            return t.DataError(errors)
        return value
    return check


def contains(trafaret):
    def check(data):
        for v in data:
            try:
                trafaret(v)
            except t.DataError:
                pass
            else:
                return data
        raise t.DataError('Array does not contains any value that completes test')
    return check


def property_names(trafaret):
    checker = t.List(trafaret)
    def check(data):
        return checker(list(data.keys()))
    return check


keywords = (
    t.Key('enum', optional=True, trafaret=t.List(t.Any) & (lambda consts: t.Or(*(t.Atom(cnst) for cnst in consts)))), # uniq?
    t.Key('const', optional=True, trafaret=t.Any() & then(t.Atom)),
    t.Key('type', optional=True, trafaret=ensure_list(json_schema_type) & then(Any)),

    # number validation
    t.Key('multipleOf', optional=True, trafaret=t.Float(gt=0) & then(multipleOf)),
    t.Key('maximum', optional=True, trafaret=t.Float() & (lambda maximum: t.Float(lte=maximum))),
    t.Key('exclusiveMaximum', optional=True, trafaret=t.Float() & (lambda maximum: t.Float(lt=maximum))),
    t.Key('minimum', optional=True, trafaret=t.Float() & (lambda minimum: t.Float(gte=minimum))),
    t.Key('exclusiveMinimum', optional=True, trafaret=t.Float() & (lambda minimum: t.Float(gt=minimum))),

    # string
    t.Key('maxLength', optional=True, trafaret=t.Int(gte=0) & (lambda length: t.String(max_length=length))),
    t.Key('minLength', optional=True, trafaret=t.Int(gte=0) & (lambda length: t.String(min_length=length))),
    t.Key('pattern', optional=True, trafaret=Pattern() & (lambda pattern: t.Regexp(pattern))),

    # array
    t.Key('maxItems', optional=True, trafaret=t.Int(gte=0) & (lambda length: t.List(t.Any, max_length=length))),
    t.Key('minItems', optional=True, trafaret=t.Int(gte=0) & (lambda length: t.List(t.Any, min_length=length))),
    t.Key('uniqueItems', optional=True, trafaret=t.Bool() & (lambda need_check: t.List(t.Any) & uniq if need_check else t.Any)),

    # object
    t.Key('maxProperties', optional=True, trafaret=t.Int(gte=0) & (lambda max_props: t.Type(dict) & (lambda props: props if len(props) <= max_props else t.DataError('Too many properties')))),
    t.Key('minProperties', optional=True, trafaret=t.Int(gte=0) & (lambda min_props: t.Type(dict) & (lambda props: props if len(props) >= min_props else t.DataError('Too few properties')))),
    t.Key('required', optional=True, trafaret=unique_strings_list & required),

    t.Key('format', optional=True, trafaret=t.Enum('date-time', 'date', 'time', 'email', 'phone', 'hostname', 'ipv4', 'ipv6', 'uri', 'uri-reference', 'uri-template', 'json-pointer')),
)

ignore_keys = {'$id', '$schema', '$ref', 'title', 'description', 'definitions', 'examples'}


def subdict(name, *keys, trafaret):
    def inner(data):
        errors = False
        preserve_output = []
        touched = set()
        collect = {}
        for key in keys:
            for k, v, names in key(data):
                touched.update(names)
                preserve_output.append((k, v, names))
                if isinstance(v, t.DataError):
                    errors = True
                else:
                    collect[k] = v
        if errors:
            yield from preserve_output
        elif collect:
            yield name, t.catch(trafaret, **collect), touched
    return inner


def check_array(*, items=[], additionalItems=None):
    if len(items) == 1:
        return t.List(items[0])

    def inner(data):
        errors = {}
        values = []
        for index, schema in enumerate(items):
            try:
                value = schema(data[index])
                values.append(value)
            except t.DataError as de:
                errors[index] = de
            except IndexError:
                errors[index] = t.DataError('value with this index is required')
        if len(items) < len(data):
            if additionalItems:
                for index in range(len(items), len(data)):
                    try:
                        value = additionalItems(data[index])
                        values.append(value)
                    except t.DataError as de:
                        errors[index] = de
            else:
                raise t.DataError('Too many items in array')
        if errors:
            raise t.DataError(errors)
        return values
    return inner


def pattern_key(regexp_str, trafaret):
    regexp = re.compile(regexp_str)

    def inner(data):
        for k, v in data.items():
            if regexp.match(k):
                yield k, t.catch(trafaret, v), (k,)
    return inner


def check_object(*, properties={}, patternProperties={}, additionalProperties=None, dependencies={}):
    keys = []
    for name, trafaret in properties.items():
        keys.append(t.Key(name, optional=True, trafaret=trafaret))
    for pattern, trafaret in patternProperties.items():
        keys.append(pattern_key(pattern, trafaret))
    additionals_trafaret = additionalProperties or t.Any
    dict_trafaret = t.Dict(*keys, allow_extra='*', allow_extra_trafaret=additionals_trafaret)

    def inner(data):
        errors = {}
        try:
            value = dict_trafaret(data)
        except t.DataError:
            raise
        for k, schema in dependencies.items():
            if k not in value:
                continue
            try:
                schema(value)
            except t.DataError as de:
                errors.update(de.as_dict())
        if errors:
            raise t.DataError(errors)
        return value

    return inner


def create_schema_parser(register):
    json_schema = t.Forward()
    metadata = (
        t.Key('$id', optional=True, trafaret=t.URL),
        t.Key('$schema', optional=True, trafaret=t.URL),
        t.Key('$ref', optional=True, trafaret=t.String),
        t.Key('title', optional=True, trafaret=t.String),
        t.Key('description', optional=True, trafaret=t.String),
        t.Key('definitions', optional=True, trafaret=t.Mapping(t.String, json_schema)),
        t.Key('examples', optional=True, trafaret=t.List(t.Any)),
        t.Key('default', optional=True, trafaret=t.Any),
    )

    schema_keywords = (
        # predicates
        t.Key('allOf', optional=True, trafaret=t.List(json_schema) & then(All)),
        t.Key('anyOf', optional=True, trafaret=t.List(json_schema) & then(Any)),
        t.Key('oneOf', optional=True, trafaret=t.List(json_schema) & then(Any)),
        t.Key('not', optional=True, trafaret=json_schema & then(Not)),
        # array
        t.Key('contains', optional=True, trafaret=json_schema & then(contains)),
        subdict(
            'array',
            t.Key('items', optional=True, trafaret=ensure_list(json_schema)),
            t.Key('additionalItems', optional=True, trafaret=json_schema),
            trafaret=check_array,
        ),
        # object
        t.Key('propertyNames', optional=True, trafaret=json_schema & then(property_names)),
        subdict(
            'object',
            t.Key('properties', optional=True, trafaret=t.Mapping(t.String, json_schema)),
            t.Key('patternProperties', optional=True, trafaret=t.Mapping(Pattern, json_schema)),
            t.Key('additionalProperties', optional=True, trafaret=json_schema),
            t.Key('dependencies', optional=True, trafaret=t.Mapping(t.String, unique_strings_list & required | json_schema)),
            trafaret=check_object,
        ),
    )

    def validate_schema(schema):
        touched_names = set()
        errors = {}
        keywords_checks = []
        for key in [*keywords, *schema_keywords]:
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
    return json_schema


def json_schema(schema, register=None):
    register = register or Register()
    return create_schema_parser(register)(schema)
