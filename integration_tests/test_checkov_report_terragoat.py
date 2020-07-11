import os
import unittest

import json

class TestCheckovResultsTerragoat(unittest.TestCase):

    def test_report(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        report_path = current_dir + "../checkov_report_terragoat.json"
        with open (report_path) as json_file:
            data = json.load(json_file)
            self.assertEqual(data["summary"]["parsing_errors"],0, "expecting 0 parsing errors")
            self.assertGreater(data["summary"]["failed"],1, "expecting more then 1 failed checks")

if __name__ == '__main__':
    unittest.main()
