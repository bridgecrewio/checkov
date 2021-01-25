import unittest
import hcl2

from checkov.terraform.checks.resource.aws.DMSReplicationInstancePubliclyAccessible import check
from checkov.common.models.enums import CheckResult


class TestDMSReplicationInstancePubliclyAccessible(unittest.TestCase):


    def test_failure_set_public(self):
        hcl_res = hcl2.loads("""
          resource "aws_dms_replication_instance" "public" {
            engine_version               = "3.1.4"
            multi_az                     = false
            publicly_accessible          = true
            replication_instance_class   = "dms.t2.micro"
            replication_instance_id      = "test-dms-replication-instance-tf"
          }
        """)
        resource_conf = hcl_res['resource'][0]['aws_dms_replication_instance']['public']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_set_private(self):
        hcl_res = hcl2.loads("""
          resource "aws_dms_replication_instance" "private" {
            engine_version               = "3.1.4"
            multi_az                     = false
            publicly_accessible          = false
            replication_instance_class   = "dms.t2.micro"
            replication_instance_id      = "test-dms-replication-instance-tf"
          }
        """)
        resource_conf = hcl_res['resource'][0]['aws_dms_replication_instance']['private']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_default(self):
        hcl_res = hcl2.loads("""
          resource "aws_dms_replication_instance" "private" {
            engine_version               = "3.1.4"
            multi_az                     = false
            replication_instance_class   = "dms.t2.micro"
            replication_instance_id      = "test-dms-replication-instance-tf"
          }
        """)
        resource_conf = hcl_res['resource'][0]['aws_dms_replication_instance']['private']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
