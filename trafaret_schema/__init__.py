import re
import sre_constants
import weakref
from uuid import uuid4
import trafaret as t


__VERSION__ = (0, 1, 0)


# Utils
#######
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


def ensure_list(typ):
    return t.List(typ) | typ & (lambda x: [x])


# JSON Schema implementation
############################
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


# simple keys that does not provide $ref headache
keywords = (
    t.Key('enum', optional=True, trafaret=t.List(t.Any) & (lambda consts: t.Or(*(t.Atom(cnst) for cnst in consts)))),
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
    t.Key(
        'uniqueItems',
        optional=True,
        trafaret=t.Bool() & (lambda need_check: t.List(t.Any) & uniq if need_check else t.Any)
    ),

    # object
    t.Key(
        'maxProperties',
        optional=True,
        trafaret=(
            t.Int(gte=0)
            & (lambda max_props: (
                t.Type(dict)
                & (lambda props: props if len(props) <= max_props else t.DataError('Too many properties'))
            ))
        )
    ),
    t.Key(
        'minProperties',
        optional=True,
        trafaret=(
            t.Int(gte=0)
            & (lambda min_props: (
                t.Type(dict)
                & (lambda props: props if len(props) >= min_props else t.DataError('Too few properties'))
            ))
        )
    ),
    t.Key('required', optional=True, trafaret=unique_strings_list & required),

    t.Key(
        'format',
        optional=True,
        trafaret=t.Enum(
            'date-time',
            'date',
            'time',
            'email',
            'phone',
            'hostname',
            'ipv4',
            'ipv6',
            'uri',
            'uri-reference',
            'uri-template',
            'json-pointer',
        )
    ),
)

ignore_keys = {'$id', '$schema', '$ref', 'title', 'description', 'definitions', 'examples'}


def subdict(name, *keys, **kw):
    trafaret = kw.pop('trafaret')  # coz py2k

    def inner(data, context=None):
        errors = False
        preserve_output = []
        touched = set()
        collect = {}
        for key in keys:
            for k, v, names in key(data, context=context):
                touched.update(names)
                preserve_output.append((k, v, names))
                if isinstance(v, t.DataError):
                    errors = True
                else:
                    collect[k] = v
        if errors:
            for out in preserve_output:
                yield out
        elif collect:
            yield name, t.catch(trafaret, **collect), touched

    return inner


def check_array(items=[], additionalItems=None):
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


def check_object(properties={}, patternProperties={}, additionalProperties=None, dependencies={}):
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


class Register(object):
    def __init__(self):
        self.schemas = {}

    def reg_schema(self, name):
        self.schemas[name] = SchemaRegister(name, self)
        return self.schemas[name]

    def get_schema(self, ref):
        schema_id, reference = ref.split('#', 1)
        if schema_id not in self.schemas:
            raise t.DataError('Bad reference `%s` in schema' % ref)
        return self.schemas[schema_id].get_schema('#' + reference)

    def validate_references(self):
        for schema in self.schemas.values():
            schema.validate_references()


class SchemaRegister(object):
    def __init__(self, name, register):
        self.name = name
        self.current_path = []
        self.schemas = {}
        self.references = set()
        self.register = weakref.ref(register)

    def save_schema(self, schema):
        assert self.str_path() not in self.schemas
        self.schemas[self.str_path()] = schema

    def get_schema(self, ref):
        if ref.startswith('#'):  # local reference
            if ref not in self.schemas:
                # TODO detect on build
                raise t.DataError('Bad reference `%s` in JSON schema' % ref)
            return self.schemas.get(ref)
        else:
            return self.register().get_schema(ref)

    def reg_reference(self, ref):
        self.references.add(ref)

    def validate_references(self):
        for reference in self.references:
            self.get_schema(reference)

    def str_path(self):
        return '#/' + '/'.join(path for path in self.current_path)

    def push(self, path):
        self.current_path.append(path)
        # print('>> ' + self.name + self.str_path())

    def pop(self):
        if self.current_path:
            self.current_path.pop()
        # print('<< ' + self.str_path())


def deep_schema(key):
    def inner(data, context=None):
        register = context
        register.push(key)
        try:
            schema = json_schema(data, context=register)
            register.save_schema(schema)
            return schema
        finally:
            register.pop()
    return t.Call(inner)


def deep_schema_mapping(path, key_trafaret):
    def inner(mapping, context=None):
        register = context
        if not isinstance(mapping, dict):
            raise t.DataError("value is not a dict", value=mapping)
        checked_mapping = {}
        errors = {}
        for key, value in mapping.items():
            pair_errors = {}
            try:
                checked_key = key_trafaret.check(key, context=register)
            except t.DataError as err:
                pair_errors['key'] = err
                checked_key = None
            try:
                if checked_key:
                    register.push(path)
                    register.push(checked_key)
                schema = json_schema.check(value, context=register)
            except t.DataError as err:
                pair_errors['value'] = err
            else:
                register.save_schema(schema)
            finally:
                if checked_key:
                    register.pop()
                    register.pop()
            if pair_errors:
                errors[key] = t.DataError(error=pair_errors)
            else:
                checked_mapping[checked_key] = schema
        if errors:
            raise t.DataError(error=errors)
        return checked_mapping
    return inner


def ref_field(reference, context=None):
    register = context
    register.reg_reference(reference)

    def inner(value, context=None):
        schema = register.get_schema(reference)
        return schema(value, context=context)

    return inner


json_schema = t.Forward()

metadata = (
    t.Key('$id', optional=True, trafaret=t.URL),
    t.Key('$schema', optional=True, trafaret=t.URL),
    t.Key('$ref', optional=True, trafaret=t.String & ref_field),
    t.Key('title', optional=True, trafaret=t.String),
    t.Key('description', optional=True, trafaret=t.String),
    t.Key('definitions', optional=True, trafaret=deep_schema_mapping('definitions', t.String())),
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
    t.Key('contains', optional=True, trafaret=deep_schema('contains') & then(contains)),
    subdict(
        'array',
        t.Key('items', optional=True, trafaret=ensure_list(json_schema)),
        t.Key('additionalItems', optional=True, trafaret=json_schema),
        trafaret=check_array,
    ),
    # object
    t.Key('propertyNames', optional=True, trafaret=deep_schema('propertyNames') & then(property_names)),
    subdict(
        'object',
        t.Key('properties', optional=True, trafaret=deep_schema_mapping('properties', t.String())),
        t.Key('patternProperties', optional=True, trafaret=deep_schema_mapping('patternProperties', Pattern())),
        t.Key('additionalProperties', optional=True, trafaret=deep_schema('additionalProperties')),
        t.Key(
            'dependencies',
            optional=True,
            trafaret=t.Mapping(t.String, unique_strings_list & required | deep_schema('dependencies'))
        ),
        trafaret=check_object,
    ),
)


all_keywords = () + metadata + keywords + schema_keywords


def validate_schema(schema, context=None):
    # we use `context` to provide register to deep schemas
    if context is None or isinstance(context, Register):
        register = context or Register()
        schema_name = schema.get('$id') or uuid4().urn
        schema_register = register.reg_schema(schema_name)
    elif isinstance(context, SchemaRegister):
        schema_register = context
    else:
        ValueError('You need to provide Register instance to json_schema and nothing else')

    touched_names = set()
    errors = {}
    keywords_checks = []
    for key in all_keywords:
        for k, v, names in key(schema, context=schema_register):
            if isinstance(v, t.DataError):
                errors[k] = v
            else:
                keywords_checks.append(v)
            touched_names = touched_names.union(names)
    # touched_names = touched_names.union(ignore_keys)
    schema_keys = set(schema.keys())
    for key in schema_keys - touched_names:
        errors[key] = '%s is not allowed key' % key
    if errors:
        raise t.DataError(errors)
    schema_trafaret = All(keywords_checks)
    return schema_trafaret


json_schema << (t.Type(dict) & t.Call(validate_schema))
