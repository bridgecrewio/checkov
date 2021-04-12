import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.VPCDefaultNetwork import check


class TestDefaultVPC(unittest.TestCase):

    def test_failure(self):
        """
          When there is a resource with aws_default_vpc, it should fail whatever the config is.
        """
        hcl_res = hcl2.loads("""
        resource "aws_default_vpc" "default" {
            tags = {
                Name = "Default VPC"
            }
        }
        """)

        resource_conf = hcl_res['resource'][0]['aws_default_vpc']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_config(self):
        """
        There is no success/pass scenario for this resource as we want to avoid the creation of this resource.
        """
        resource_conf = {
            "enable_dns_support": "true"
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
