import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.DocDBTLS import check


class TestDocDBTLS(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_docdb_cluster_parameter_group" "test" {
                  family      = "docdb3.6"
                  name        = "test"
                  description = "docdb cluster parameter group"

                  parameter {
                    name  = "tls"
                    value = "disabled"
                  }

                  parameter {
                    name  = "other-param"
                    value = "enabled"
                  }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_docdb_cluster_parameter_group']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_no_parameters(self):
        hcl_res = hcl2.loads("""
                resource "aws_docdb_cluster_parameter_group" "test" {
                  family      = "docdb3.6"
                  name        = "test"
                  description = "docdb cluster parameter group"
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_docdb_cluster_parameter_group']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_with_parameters(self):
        hcl_res = hcl2.loads("""
                resource "aws_docdb_cluster_parameter_group" "test" {
                  family      = "docdb3.6"
                  name        = "test"
                  description = "docdb cluster parameter group"

                  parameter {
                    name  = "tls"
                    value = "enabled"
                  }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_docdb_cluster_parameter_group']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
