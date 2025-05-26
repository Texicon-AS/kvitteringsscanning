"""
@brief Unit Tests for Kassalappen parser, to ensure that edge cases are taken care of.
"""

import unittest
import os
import json
import tempfile

from kassalappen.parser import appendToJsonFile # type: ignore


class TestKassalappenParser(unittest.TestCase):

    def setUp(self):
        self.file_path = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()))

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.unlink(self.file_path)

    def testNewFileCreation(self):
        data = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
        useful_fields = ["id", "name"]

        appendToJsonFile(self.file_path, data, useful_fields)

        with open(self.file_path, "r") as f:
            content = json.load(f)

        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]["id"], 1)
        self.assertEqual(content[0]["name"], "John")
        self.assertEqual(content[1]["id"], 2)
        self.assertEqual(content[1]["name"], "Jane")

    def testAppendToExistingFile(self):

        initial_data = [
            {"id": 1, "name": "John"},
        ]
        with open(self.file_path, 'w') as f:
            json.dump(initial_data,f)
        

        new_data = [{"id": 2, "name": "Jane"}]
        useful_fields = ["id", "name"]

        appendToJsonFile(self.file_path, new_data, useful_fields)

        with open(self.file_path, "r") as f:
            content = json.load(f)

        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]["id"], 1)
        self.assertEqual(content[0]["name"], "John")
        self.assertEqual(content[1]["id"], 2)
        self.assertEqual(content[1]["name"], "Jane")

    def testMissingFields(self):
        data = [{"id": 1, "name": "John"}, {"id": 2, "extra": "value"}]
        useful_fields = ["id", "name"]

        appendToJsonFile(self.file_path, data, useful_fields)

        with open(self.file_path, "r") as f:
            content = json.load(f)

        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]["id"], 1)
        self.assertEqual(content[0]["name"], "John")
        self.assertEqual(content[1]["id"], 2)
        self.assertFalse(content[1]["name"], "Jane")

    def testEmptyData(self):
        data = []
        useful_fields = ["id", "name"]

        appendToJsonFile(self.file_path, data, useful_fields)

        with open(self.file_path, "r") as f:
            content = json.load(f)


        self.assertEqual(len(content), 0)

    def testMultipleAppends(self):
        # First append
        data1 = [{"id": 1, "name": "John"}]
        useful_fields = ["id", "name"]
        appendToJsonFile(self.file_path, data1, useful_fields)
        
        # Second append
        data2 = [{"id": 2, "name": "Jane"}]
        appendToJsonFile(self.file_path, data2, useful_fields)
        
        # Third append
        data3 = [{"id": 3, "name": "Bob"}]
        appendToJsonFile(self.file_path, data3, useful_fields)
        
        with open(self.file_path, 'r') as f:
            content = json.load(f)
            
        self.assertEqual(len(content), 3)
        self.assertEqual([item["id"] for item in content], [1, 2, 3])
        self.assertEqual([item["name"] for item in content], ["John", "Jane", "Bob"])


    def testMultipleAppendsWithMixedData(self):
        data1 = [{"id": 1, "name": "John"}]
        useful_fields = ["id", "name"]
        appendToJsonFile(self.file_path, data1, useful_fields)
        
        data2 = [{"id": 2, "name": "Jane"}]
        appendToJsonFile(self.file_path, data2, useful_fields)
        
        data_empty = []
        appendToJsonFile(self.file_path, data_empty, useful_fields)

        data3 = [{"id": 3, "name": "Bob"}]
        appendToJsonFile(self.file_path, data3, useful_fields)
        
        with open(self.file_path, 'r') as f:
            content = json.load(f)
            
        self.assertEqual(len(content), 3)
        self.assertEqual([item["id"] for item in content], [1, 2, 3])


if __name__ == '__main__':
    unittest.main()