import unittest
import hcl2

from checkov.terraform.checks.resource.aws.DBInstanceMonitoring import check
from checkov.common.models.enums import CheckResult


class TestDBInstanceMonitoring(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                    resource "aws_db_instance" "example" {                    
                      allocated_storage = 10
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_db_instance']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                    resource "aws_db_instance" "example" {                    
                      allocated_storage = 10
                      monitoring_role_arn = "iam_role_arn"
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_db_instance']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
