import json
import os
import unittest

current_dir = os.path.dirname(os.path.realpath(__file__))


class TestCheckovConfig(unittest.TestCase):

    def test_github_configuration_report(self):
        # Report to be generated using following command:
        # checkov -d path/to/terragoat --config-file \
        # path/to/checkov/integration_tests/example_config_files/config.yaml \
        # > path/to/checkov/checkov_config_report_terragoat.json
        report_path = os.path.join(os.path.dirname(current_dir), "checkov_report_github_config.json")
        with open(report_path) as json_file:
            print(f"Got checkov_report_github_config result: {json_file}\n")
            data = json.load(json_file)
            self.assertEqual(data["summary"]["parsing_errors"], 0,
                             f"expecting 0 parsing errors but got: {data['results']['parsing_errors']}")
            self.assertEqual(data["summary"]["failed"], 3,
                               f"expecting 3 failed checks, got: {data['summary']['failed']}")
            self.assertEqual(data['check_type'], 'github_configuration',
                             f"expecting 'github_configuration' but got: {data['check_type']}")
            self.assertEqual(data['results']['failed_checks'][0]['check_id'], 'CKV_GITHUB_3',
                             f"expecting a fail on 'CKV_GITHUB_3' but got: {data['results']['failed_checks'][0]['check_id']}")
            self.assertEqual(data['results']['failed_checks'][1]['check_id'], 'CKV_GITHUB_2',
                             f"expecting a fail on 'CKV_GITHUB_2' but got: {data['results']['failed_checks'][0]['check_id']}")
            self.assertEqual(data['results']['failed_checks'][2]['check_id'], 'CKV_GITHUB_1',
                             f"expecting a fail on 'CKV_GITHUB_1' but got: {data['results']['failed_checks'][0]['check_id']}")


if __name__ == '__main__':
    unittest.main()
