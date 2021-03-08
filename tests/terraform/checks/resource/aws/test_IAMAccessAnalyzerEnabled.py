import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.IAMAccessAnalyzerEnabled import check
import hcl2


class TestIAMAccessAnalyzerEnabled(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "aws_accessanalyzer_analyzer" "example" {
         depends_on = [aws_organizations_organization.example]
    
         type          = "ORGANIZATION"
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_accessanalyzer_analyzer']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "aws_accessanalyzer_analyzer" "example" {
         depends_on = [aws_organizations_organization.example]
    
         analyzer_name = "example"
         type          = "ORGANIZATION"
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_accessanalyzer_analyzer']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
