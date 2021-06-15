import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.TransferServerIsPublic import check
import hcl2


class TestTransferServerIsPublic(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_transfer_server" "example" {
                    endpoint_type = "PUBLIC"

                    protocols   = ["SFTP"]
                }
            """)
        resource_conf = hcl_res['resource'][0]['aws_transfer_server']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_transfer_server" "example" {
                    endpoint_type = "VPC"

                    protocols   = ["SFTP"]
                }
            """)
        resource_conf = hcl_res['resource'][0]['aws_transfer_server']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
