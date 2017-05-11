Trafaret Schema
===============

Project takes json schema and converts it to Trafaret instance:

    from trafaret_schema import json_schema
    check_string = json_schema({'type': 'string', 'minLength': 6, 'maxLength': 10, 'pattern': '(bla)+'})
    check_string('blablabla')
