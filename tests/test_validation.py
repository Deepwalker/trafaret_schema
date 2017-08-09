import unittest
import trafaret as t
import trafaret_schema


class TestConstEnumType(unittest.TestCase):
    def test_const(self):
        check = trafaret_schema.json_schema({
            'const': 'blabla',
        })
        self.assertEqual(check('blabla'), 'blabla')

        check = trafaret_schema.json_schema({
            'const': 100,
        })
        self.assertEqual(check(100), 100)

    def test_enum(self):
        check = trafaret_schema.json_schema({
            'enum': ['blabla', 200],
        })
        self.assertEqual(check('blabla'), 'blabla')
        self.assertEqual(check(200), 200)
        with self.assertRaises(t.DataError):
            check(300)

    def test_type(self):
        check = trafaret_schema.json_schema({'type': 'null'})
        self.assertEqual(check(None), None)

        check = trafaret_schema.json_schema({'type': 'boolean'})
        self.assertEqual(check(True), True)

        check = trafaret_schema.json_schema({'type': 'object'})
        self.assertEqual(check({}), {})

        check = trafaret_schema.json_schema({'type': 'array'})
        self.assertEqual(check([]), [])

        check = trafaret_schema.json_schema({'type': 'number'})
        self.assertEqual(check(2.4), 2.4)

        check = trafaret_schema.json_schema({'type': 'integer'})
        self.assertEqual(check(200), 200)
        with self.assertRaises(t.DataError):
            check('blabla')

        check = trafaret_schema.json_schema({'type': 'string'})
        self.assertEqual(check('a'), 'a')


class TestPredicates(unittest.TestCase):
    def test_all_of(self):
        check = trafaret_schema.json_schema({
            'allOf': [
                {'minLength': 5},
                {'maxLength': 10},
            ],
        })
        self.assertEqual(check('blabla'), 'blabla')
        with self.assertRaises(t.DataError):
            check('bla')

    def test_any_of(self):
        check = trafaret_schema.json_schema({
            'anyOf': [
                {'minLength': 5},
                {'maxLength': 3},
            ],
        })
        self.assertEqual(check('blabla'), 'blabla')
        self.assertEqual(check('bla'), 'bla')
        with self.assertRaises(t.DataError):
            check('blab')

    def test_not(self):
        check = trafaret_schema.json_schema({
            'not': {'minLength': 5},
        })
        self.assertEqual(check('bla'), 'bla')
        with self.assertRaises(t.DataError):
            check('blabla')



class TestStringValidation(unittest.TestCase):
    def test_string(self):
        check = trafaret_schema.json_schema({
            'type': 'string',
        })
        self.assertEqual(check('blabla'), 'blabla')

    def test_min_length(self):
        check = trafaret_schema.json_schema({
            'type': 'string',
            'minLength': 60,
        })
        with self.assertRaises(t.DataError):
            check('blabla')

    def test_max_length(self):
        check = trafaret_schema.json_schema({
            'type': 'string',
            'maxLength': 5,
        })
        with self.assertRaises(t.DataError):
            check('blabla')

    def test_pattern(self):
        check = trafaret_schema.json_schema({
            'type': 'string',
            'pattern': 'bla+',
            'maxLength': 10,
            'minLength': 5,
        })
        self.assertEqual(check('blablabla'), 'blablabla')


class TestNumberValidation(unittest.TestCase):
    def test_number(self):
        check = trafaret_schema.json_schema({
            'type': 'integer',
        })
        self.assertEqual(check(100), 100)
        with self.assertRaises(t.DataError):
            check(100.4)

    def test_minimum(self):
        check = trafaret_schema.json_schema({
            'type': 'number',
            'minimum': 5,
        })
        with self.assertRaises(t.DataError):
            check(1)

        check = trafaret_schema.json_schema({
            'type': 'number',
            'exclusiveMinimum': 5,
        })
        with self.assertRaises(t.DataError):
            check(5)

    def test_maximum(self):
        check = trafaret_schema.json_schema({
            'type': 'number',
            'maximum': 5,
        })
        with self.assertRaises(t.DataError):
            check(10)

        check = trafaret_schema.json_schema({
            'type': 'number',
            'exclusiveMaximum': 5,
        })
        with self.assertRaises(t.DataError):
            check(5)

    def test_multiple_of(self):
        check = trafaret_schema.json_schema({
            'type': 'number',
            'multipleOf': 5,
        })
        self.assertEqual(check(10), 10)
        with self.assertRaises(t.DataError):
            check(11)


class TestArrays(unittest.TestCase):
    def test_min_items(self):
        check = trafaret_schema.json_schema({
            'type': 'array',
            'minItems': 5,
        })
        with self.assertRaises(t.DataError):
            check([1,2,3,4])
        self.assertEqual(check([1,2,3,4,5]), [1,2,3,4,5])

    def test_max_items(self):
        check = trafaret_schema.json_schema({
            'type': 'array',
            'maxItems': 5,
        })
        with self.assertRaises(t.DataError):
            check([1,2,3,4,5,6])
        self.assertEqual(check([1,2,3,4,5]), [1,2,3,4,5])

    def test_uniq(self):
        check = trafaret_schema.json_schema({
            'type': 'array',
            'uniqueItems': True,
        })
        with self.assertRaises(t.DataError):
            check([1,2,3,4,5,5])
        self.assertEqual(check([1,2,3,4,5]), [1,2,3,4,5])

    def test_contains(self):
        check = trafaret_schema.json_schema({
            'type': 'array',
            'contains': {'type': 'number'},
        })
        with self.assertRaises(t.DataError):
            check(['a','b','c'])
        self.assertEqual(check(['a','b','c',5]), ['a','b','c',5])

    def test_simple_items(self):
        check = trafaret_schema.json_schema({
            'type': 'array',
            'items': {'type': 'number'},
        })
        with self.assertRaises(t.DataError):
            check([1,2,'a',4,5,5])
        self.assertEqual(check([1,2,3,4,5]), [1,2,3,4,5])

    def test_positional_items(self):
        check = trafaret_schema.json_schema({
            'type': 'array',
            'items': [{'type': 'number'}, {'type': 'string'}],
        })
        with self.assertRaises(t.DataError):
            # bad 2nd position
            check([1,None])
        with self.assertRaises(t.DataError):
            # too long array
            check([1,'a',4,5,5])
        self.assertEqual(check([1,'a']), [1,'a'])

    def test_additional_items(self):
        check = trafaret_schema.json_schema({
            'type': 'array',
            'items': [{'type': 'number'}, {'type': 'string'}],
            'additionalItems': {'type': 'number'},
        })
        with self.assertRaises(t.DataError):
            check([1,None,4,5,5])
        with self.assertRaises(t.DataError):
            check([1,'a','a',5,5])
        self.assertEqual(check([1,'a',5,5,5]), [1,'a',5,5,5])


class TestObjects(unittest.TestCase):
    def test_max_props(self):
        check = trafaret_schema.json_schema({
            'type': 'object',
            'maxProperties': 1,
        })
        with self.assertRaises(t.DataError):
            check({'a': 1, 'b': 2})
        self.assertEqual(check({'a': 1}), {'a': 1})

    def test_min_props(self):
        check = trafaret_schema.json_schema({
            'type': 'object',
            'minProperties': 2,
        })
        with self.assertRaises(t.DataError):
            check({'a': 1})
        self.assertEqual(check({'a': 1, 'b': 2}), {'a': 1, 'b': 2})

    def test_required(self):
        check = trafaret_schema.json_schema({
            'type': 'object',
            'required': ['a', 'b'],
        })
        with self.assertRaises(t.DataError):
            check({'a': 1})
        self.assertEqual(check({'a': 1, 'b': 2}), {'a': 1, 'b': 2})

    def test_properties(self):
        check = trafaret_schema.json_schema({
            'type': 'object',
            'properties': {'a': {'type': 'number'}},
        })
        with self.assertRaises(t.DataError):
            check({'a': 'b'})
        self.assertEqual(check({'a': 1, 'b': 2}), {'a': 1, 'b': 2})

    def test_pattern_properties(self):
        check = trafaret_schema.json_schema({
            'type': 'object',
            'patternProperties': {'a+': {'type': 'number'}},
        })
        with self.assertRaises(t.DataError):
            check({'a': 'b'})
        with self.assertRaises(t.DataError):
            check({'a': 3, 'aaa': 'b'})
        self.assertEqual(check({'a': 1, 'aaa': 3}), {'a': 1, 'aaa': 3})

    def test_additional_properties(self):
        check = trafaret_schema.json_schema({
            'type': 'object',
            'properties': {'a': {'type': 'number'}},
            'additionalProperties': {'type': 'boolean'},
        })
        with self.assertRaises(t.DataError):
            check({'a':1, 'b': 2})
        self.assertEqual(check({'a': 1, 'b': True}), {'a': 1, 'b': True})

    def test_property_names(self):
        check = trafaret_schema.json_schema({
            'type': 'object',
            'propertyNames': {
                'type': 'string',
                'pattern': 'bla+',
            },
        })
        with self.assertRaises(t.DataError):
            check({'a': 'b'})
        self.assertEqual(check({'bla': 1, 'blabla': 3}), {'bla': 1, 'blabla': 3})

    def test_dependencies(self):
        check = trafaret_schema.json_schema({
            'type': 'object',
            'properties': {'a': {'type': 'number'}},
            'dependencies': {'a': ['b', 'c']},
        })
        self.assertEqual(check({'bla': 1, 'blabla': 3}), {'bla': 1, 'blabla': 3})
        with self.assertRaises(t.DataError):
            check({'a': 'b'})
        self.assertEqual(check({'a': 1, 'b': 3, 'c': 4}), {'a': 1, 'b': 3, 'c': 4})


class TestReferences(unittest.TestCase):
    def test_local_reference(self):
        check = trafaret_schema.json_schema({
            'type': 'object',
            "properties": {
                "billing_address": { "$ref": "#/definitions/address" },
                "shipping_address": { "$ref": "#/definitions/address" },
            },
            "definitions": {
                "address": {
                    "type": "object",
                    "properties": {
                        "street_address": { "type": "string" },
                        "city": { "type": "string" },
                        "state": { "type": "string" },
                    },

                    "required": ["city"],
                },
            },
        })
        data = {
            'billing_address': {'city': 'Samara'},
            'shipping_address': {'city': 'Samara'},
        }
        assert check(data) == data

    def test_adjacent_reference(self):
        register = trafaret_schema.Register()
        addresses = trafaret_schema.json_schema({
                "$id": "http://yuhuhu.com/address",
                "type": "object",
                "properties": {
                    "billing_address": { "$ref": "#/definitions/address" },
                    "shipping_address": { "$ref": "#/definitions/address" },
                },
                "definitions": {
                    "address": {
                        "type": "object",
                        "properties": {
                            "street_address": { "type": "string" },
                            "city": { "type": "string" },
                            "state": { "type": "string" },
                        },

                        "required": ["city"],
                    },
                },
            },
            context=register,
        )
        person = trafaret_schema.json_schema({
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"$ref":  "http://yuhuhu.com/address#/definitions/address"},
                },
            },
            context=register,
        )

        data = {
            'name': 'Peotr',
            'address': {'city': 'Moscow'},
        }
        assert person.check(data) == data

        register.validate_references()


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
