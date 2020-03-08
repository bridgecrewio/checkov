import unittest

from checkov.terraform.checks.resource.aws.CloudtrailLogValidation import check
from checkov.common.models.enums import CheckResult


class TestCloudtrailLogValidation(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'enable_logging': [True], 's3_bucket_name': ['${foo}'],
                         'is_multi_region_trail': [True], 'include_global_service_events': [True],
                         'name': ['foo']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'enable_logging': [True], 's3_bucket_name': ['${foo}'], 'enable_log_file_validation': [True],
                         'is_multi_region_trail': [True], 'include_global_service_events': [True],
                         'kms_key_id': ['${foo}'], 'name': ['foo']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
