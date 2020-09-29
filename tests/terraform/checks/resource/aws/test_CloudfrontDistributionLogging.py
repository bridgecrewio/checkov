import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.CloudfrontDistributionLogging import check


class TestCloudfrontDistributionLogging(unittest.TestCase):

    def test_failure(self):
        resource_conf = {
            "comment": "Example",
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "comment": "Example",
            "logging_config": [
                {
                    "bucket": "some-arn"
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
