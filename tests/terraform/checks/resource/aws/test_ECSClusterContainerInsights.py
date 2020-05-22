import unittest

from checkov.terraform.checks.resource.aws.ECSClusterContainerInsights import check
from checkov.common.models.enums import CheckResult


class TestECSClusterContainerInsights(unittest.TestCase):

    def test_failure(self):
        resource_conf = {
            "name": ["white-hart"]
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": ["white-hart"],
            "setting": {"name": "containerInsights", "value": "enabled"}
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
