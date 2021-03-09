import unittest
import hcl2

from checkov.terraform.checks.resource.aws.SageMakerInternetAccessDisabled import check
from checkov.common.models.enums import CheckResult


class TestSageMakerInternetAccessDisabled(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_sagemaker_notebook_instance" "test" {
                  name          = "my-notebook-instance"
                  role_arn      = aws_iam_role.role.arn
                  instance_type = "ml.t2.medium"
                  direct_internet_access = "Enabled"
                                    
                  tags = {
                    Name = "foo"
                  }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_sagemaker_notebook_instance']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_sagemaker_notebook_instance" "test" {
                  name          = "my-notebook-instance"
                  role_arn      = aws_iam_role.role.arn
                  instance_type = "ml.t2.medium"
                  direct_internet_access = "Disabled"
                                  
                  tags = {
                    Name = "foo"
                  }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_sagemaker_notebook_instance']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success2(self):
        hcl_res = hcl2.loads("""
                resource "aws_sagemaker_notebook_instance" "test" {
                  name          = "my-notebook-instance"
                  role_arn      = aws_iam_role.role.arn
                  instance_type = "ml.t2.medium"
                                  
                  tags = {
                    Name = "foo"
                  }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_sagemaker_notebook_instance']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
