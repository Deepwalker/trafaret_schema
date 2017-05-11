import unittest
import trafaret as t
import trafaret_schema


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


