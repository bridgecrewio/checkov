import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.AthenaWorkgroupConfiguration import check


class TestAthenaWorkgroupConfiguration(unittest.TestCase):

    def test_failure(self):
        resource_conf = {
            "name": "Example",
            "configuration": [
                {
                    "enforce_workgroup_configuration": False,
                }
            ],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": "Example",
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_full(self):
        resource_conf = {
            "name": "Example",
            "configuration": [
                {
                    "enforce_workgroup_configuration": True,
                }
            ],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
