import unittest

from checkov.terraform.checks.resource.gcp.GKENodePoolAutoRepairEnabled import check
from checkov.common.models.enums import CheckResult


class GKENodePoolAutoRepairEnabled(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'cluster': [''], 'management': [{}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'cluster': [''], 'management': [{'auto_repair': [True]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
