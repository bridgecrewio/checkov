import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.ECRImmutableTags import check


class TestECRImmutableTags(unittest.TestCase):
    def test_failure(self):
        resource_conf = {"name": ["bar"]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {"image_tag_mutability": ["IMMUTABLE"], "name": ["bar"]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
