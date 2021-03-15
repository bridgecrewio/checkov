import unittest
import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.RedShiftSSL import check


class TestRedShiftSSL(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_redshift_parameter_group" "examplea" {
                  name   = var.param_group_name
                  family = "redshift-1.0"
                  
                  parameter {
                    name  = "require_ssl"
                    value = "false"
                  }
                  
                  parameter {
                    name  = "enable_user_activity_logging"
                    value = "true"
                  }
                }

        """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_parameter_group']['examplea']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_no_parameters(self):
        hcl_res = hcl2.loads("""
                resource "aws_redshift_parameter_group" "examplea" {
                  name   = var.param_group_name
                  family = "redshift-1.0"
                  
                }
       """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_parameter_group']['examplea']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_with_parameters(self):
        hcl_res = hcl2.loads("""
                resource "aws_redshift_parameter_group" "examplea" {
                  name   = var.param_group_name
                  family = "redshift-1.0"
                  
                  parameter {
                    name  = "require_ssl"
                    value = "true"
                  }
                  
                  parameter {
                    name  = "enable_user_activity_logging"
                    value = "true"
                  }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_parameter_group']['examplea']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
