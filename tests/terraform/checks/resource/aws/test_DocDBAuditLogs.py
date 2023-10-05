import unittest
import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.DocDBAuditLogs import check


class TestDocDBAuditLogs(unittest.TestCase):

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
                    name  = "audit_logs"
                    value = "disabled"
                  }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_docdb_cluster_parameter_group']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_no_parameters(self):
        hcl_res = hcl2.loads("""
                resource "aws_docdb_cluster_parameter_group" "test" {
                  family      = "docdb3.6"
                  name        = "test"
                  description = "docdb cluster parameter group"
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_docdb_cluster_parameter_group']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_with_parameters(self):
        for accepted_value in ["enabled", "ddl", "all", "ddl, dml_write"]:
            hcl_res = hcl2.loads(f"""
                    resource "aws_docdb_cluster_parameter_group" "test" {{
                      family      = "docdb3.6"
                      name        = "test"
                      description = "docdb cluster parameter group"

                      parameter {{
                        name  = "audit_logs"
                        value = "{accepted_value}"
                      }}
                    }}
            """)
            resource_conf = hcl_res['resource'][0]['aws_docdb_cluster_parameter_group']['test']
            scan_result = check.scan_resource_conf(conf=resource_conf)
            self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
