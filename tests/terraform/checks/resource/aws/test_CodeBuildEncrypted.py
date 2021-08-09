import unittest
import hcl2

from checkov.terraform.checks.resource.aws.CodeBuildEncrypted import check
from checkov.common.models.enums import CheckResult


class TestCodeBuildEncrypted(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "aws_codebuild_project" "example" {
              name          = "test-project"
              description   = "test_codebuild_project"
              build_timeout = "5"
              service_role  = aws_iam_role.example.arn
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_codebuild_project']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "aws_codebuild_project" "example" {
              name          = "test-project"
              description   = "test_codebuild_project"
              build_timeout = "5"
              service_role  = aws_iam_role.example.arn
              
              encryption_key = "AWS_Key_Management_Service_example"
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_codebuild_project']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
