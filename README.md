Trafaret Schema
===============

Project takes json schema and converts it to Trafaret instance:

    from trafaret_schema import json_schema
    check_string = json_schema({'type': 'string', 'minLength': 6, 'maxLength': 10, 'pattern': '(bla)+'})
    check_string('blablabla')

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
    [ ] format
    [*] references
        [*] definitions
        [*] $ref
