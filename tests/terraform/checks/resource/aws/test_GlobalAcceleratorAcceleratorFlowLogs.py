import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.GlobalAcceleratorAcceleratorFlowLogs import check


class TestGlobalAcceleratorAcceleratorFlowLogs(unittest.TestCase):

    def test_failure(self):
        resource_conf = {"name": "Example"}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_full(self):
        resource_conf = {
            "name": "Example",
            "attributes": [
                {
                    "flow_logs_enabled": [False]
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": "Example",
            "attributes": [
                {
                    "flow_logs_enabled": [True]
                }
            ],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
