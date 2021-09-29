import json
import os
import unittest

current_dir = os.path.dirname(os.path.realpath(__file__))


class TestCheckovConfig(unittest.TestCase):

    def test_terragoat_report(self):
        # Report to be generated using following command:
        # checkov -d path/to/terragoat --config-file \
        # path/to/checkov/integration_tests/example_config_files/config.yaml \
        # > path/to/checkov/checkov_config_report_terragoat.json
        report_path = os.path.join(os.path.dirname(current_dir), "checkov_config_report_terragoat.json")
        with open(report_path) as json_file:
            data = json.load(json_file)
            self.assertEqual(data["summary"]["parsing_errors"], 0,
                             f"expecting 0 parsing errors but got: {data['results']['parsing_errors']}")
            self.assertGreater(data["summary"]["failed"], 1,
                               f"expecting more than 1 failed checks, got: {data['summary']['failed']}")
            self.assertEqual(data['check_type'], 'terraform',
                             f"expecting 'terraform' but got: {data['check_type']}")
            self.assertNotIn('guideline', data['results']['failed_checks'][0].keys(),
                             "expecting no guideline for checks.")


if __name__ == '__main__':
    unittest.main()
