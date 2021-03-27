import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.DocDBLogging import check


class TestDocDBLogging(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "cluster_identifier": "my-docdb-cluster",
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_partial(self):
        resource_conf = {
            "cluster_identifier": "my-docdb-cluster",
            "enabled_cloudwatch_logs_exports": ["audit"],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "cluster_identifier": "my-docdb-cluster",
            "enabled_cloudwatch_logs_exports": ["audit", "profiler"],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
