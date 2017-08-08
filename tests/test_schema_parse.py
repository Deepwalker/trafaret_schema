import os
import os.path as op
import unittest
import json
import trafaret_schema


class TestSchemas(unittest.TestCase):
    current_dir = op.dirname(__file__)
    schema_dir = op.join(current_dir, '../schemas')


    def test_schemas(self):
        for root, dirs, files in os.walk(self.schema_dir):
            for filename in files:
                path = op.join(root, filename)
                with open(path) as f:
                    schema = json.load(f)
                    print('Check', path)
                    trafaret_schema.json_schema(schema)
