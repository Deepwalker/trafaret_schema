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
