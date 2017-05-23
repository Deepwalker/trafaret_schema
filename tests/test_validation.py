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


class TestObjects(unittest.TestCase):
    def test_max_props(self):
        check = trafaret_schema.json_schema({
            'type': 'object',
            'maxProperties': 1,
        })
        with self.assertRaises(t.DataError):
            check({'a': 1, 'b': 2})
        self.assertEqual(check({'a': 1}), {'a': 1})
        check({'a': 1, 'b': 2})

