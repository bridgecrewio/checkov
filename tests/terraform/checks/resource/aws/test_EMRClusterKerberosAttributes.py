import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.EMRClusterKerberosAttributes import check
import hcl2


class TestEMRClusterKerberosAttributes(unittest.TestCase):

    def test_skipped_no_kerberos(self):
        hcl_res = hcl2.loads("""
resource "aws_emr_cluster" "test" {
  name          = "emr-test-arn"
  release_label = "emr-4.6.0"
  applications  = ["Spark"]

  termination_protection            = false
  keep_job_flow_alive_when_no_steps = true

  ec2_attributes {
    subnet_id                         = aws_subnet.main.id
    emr_managed_master_security_group = aws_security_group.sg.id
    emr_managed_slave_security_group  = aws_security_group.sg.id
    instance_profile                  = aws_iam_instance_profile.emr_profile.arn
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_emr_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
resource "aws_emr_cluster" "test" {
  name          = "emr-test-arn"
  release_label = "emr-4.6.0"
  applications  = ["Spark"]

  termination_protection            = false
  keep_job_flow_alive_when_no_steps = true

  kerberos_attributes {
    kdc_admin_password                = "somePassword"  # checkov:skip=CKV_SECRET_6 test secret
    realm                             = "EC2.INTERNAL"
    }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_emr_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)
        
    def test_failure(self):
        hcl_res = hcl2.loads("""
resource "aws_emr_cluster" "test" {
  name          = "emr-test-arn"
  release_label = "emr-4.6.0"
  applications  = ["Spark"]

  termination_protection            = false
  keep_job_flow_alive_when_no_steps = true

  kerberos_attributes {
    kdc_admin_password                = "somePassword"
    }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_emr_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)           


if __name__ == '__main__':
    unittest.main()
