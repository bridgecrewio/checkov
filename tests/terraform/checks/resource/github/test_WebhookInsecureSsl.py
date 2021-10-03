import unittest

import hcl2
from checkov.terraform.checks.resource.github.WebhookInsecureSsl import check
from checkov.common.models.enums import CheckResult


class TestWebhookInsecureSsl(unittest.TestCase):

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "github_repository_webhook" "foo" {
        repository = github_repository.repo.name
        name = "web"
        configuration {
            insecure_ssl = false
        }
        }
        """)
        resource_conf = hcl_res['resource'][0]['github_repository_webhook']['foo']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "github_repository_webhook" "foo" {
        repository = github_repository.repo.name
        name = "web"
        configuration {
            insecure_ssl = true
        }
        }
        """)
        resource_conf = hcl_res['resource'][0]['github_repository_webhook']['foo']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
