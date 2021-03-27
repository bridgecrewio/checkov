import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.ElasticsearchDomainEnforceHTTPS import check


class TestElasticsearchDomainEnforceHTTPS(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "domain_name": "Example",
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_explicit(self):
        resource_conf = {
            "domain_name": "Example",
            "domain_endpoint_options": [{"enforce_https": False}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "domain_name": "Example",
            "domain_endpoint_options": [{"enforce_https": True}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
