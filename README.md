Trafaret Schema
===============

[![Build status](https://circleci.com/gh/Deepwalker/trafaret.svg?style=shield)](https://circleci.com/gh/Deepwalker/trafaret)
[![Gitter](https://badges.gitter.im/Deepwalker/trafaret.png)](https://gitter.im/Deepwalker/trafaret)
[![Downloads](https://img.shields.io/pypi/v/trafaret.svg?style=flat-square)](https://pypi.python.org/pypi/trafaret)
[![Downloads](https://img.shields.io/pypi/l/trafaret.svg?style=flat-square)](https://pypi.python.org/pypi/trafaret)


Project takes JSON Schema and converts it to Trafaret instance:

    from trafaret_schema import json_schema
    check_string = json_schema({'type': 'string', 'minLength': 6, 'maxLength': 10, 'pattern': '(bla)+'})
    check_string('blablabla')

What is important to note, that this project is big trafaret that produces other trafaret. So on parsing
JSON Schema you can get DataError, and you will get DataError in usage of parsed schema.
And you can use schema parser or parsed schema as trafaret in any circumstances where you can use trafarets.

You can use `Register` object to provide custom `format` implementation and to support cross schemas `$ref`
objects:

    import trafaret as t
    from trafaret_schema import json_schema, Register

    my_reg = Register()

    my_reg.reg_format('any_ip', t.IPv4 | t.IPv6)

    check_address = json_schema(open('address.json').read(), context=register)
    check_person = json_schema(open('person.json').read(), context=register)


Project is a bit of fun, because it implemented in `trafaret` and produces `trafaret` instances. Also its like
a pro level of `trafaret` usage (I hope so).

Features:

    [*] basic
        [*] type
        [*] enum
        [*] const
        [*] number
        [*] string
    [*] array
        [*] minProperties
        [*] maxProperties
        [*] uniqueItems
        [*] items
        [*] additionalItems
        [*] contains
    [*] objects
        [*] maxProperties
        [*] minProperties
        [*] required
        [*] properties
        [*] patternProperties
        [*] additionalProperties
        [*] dependencies
        [*] propertyNames
    [*] combinators
        [*] anyOf
        [*] allOf
        [*] oneOf
        [*] not
    [*] format
    [*] references
        [*] definitions
        [*] $ref
