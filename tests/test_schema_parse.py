import os
import os.path as op
import unittest
import json
import trafaret_schema


class TestSchemas(unittest.TestCase):
    current_dir = op.dirname(__file__)
    schema_dir = op.join(current_dir, '../schemas')


    def test_schemas(self):
        for dir_entry in os.scandir(self.schema_dir):
            if dir_entry.is_file():
                with open(dir_entry.path) as f:
                    schema = json.load(f)
                    print('Check', dir_entry.path)
                    trafaret_schema.json_schema(schema)
