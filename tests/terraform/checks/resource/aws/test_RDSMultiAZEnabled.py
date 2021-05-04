import unittest
import hcl2

from checkov.terraform.checks.resource.aws.RDSMultiAZEnabled import check
from checkov.common.models.enums import CheckResult


class TestRDSMultiAZEnabled(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "aws_db_instance" "default" {
          name                   = "name"
          engine                 = "mysql"
        
          identifier              = "id"
          instance_class          = "foo"
          multi_az                = false
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_db_instance']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
        resource "aws_db_instance" "default" {
          name                   = "name"
          engine                 = "mysql"

          identifier              = "id"
          instance_class          = "foo"
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_db_instance']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "aws_db_instance" "default" {
          name                   = "name"
          engine                 = "mysql"

          identifier              = "id"
          instance_class          = "foo"
          multi_az                = true
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_db_instance']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
