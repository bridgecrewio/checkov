import unittest

from checkov.terraform.checks.resource.aws.SecurityGroupRuleDescription import check
from checkov.terraform.models.enums import CheckResult


class TestSecurityGroupRuleDescription(unittest.TestCase):

    def test_failure(self):
        resource_conf = {
            "name": "allow_ssh",
            "vpc_id": "${aws_vpc.main.id}",
            "ingress": {
                # TLS (change to whatever ports you need),
                "from_port": 22,
                "to_port": 22,
                "protocol": "-1",
                "cidr_blocks": ['0.0.0.0/0'],
            },

            "egress": {
                "from_port": 0,
                "to_port": 0,
                "protocol": "-1",
                "cidr_blocks": ["0.0.0.0/0"],
                "prefix_list_ids": ["pl-12c4e678"],
            }
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": "allow_ssh",
            "description": "Allow SSH inbound traffic",
            "vpc_id": "${aws_vpc.main.id}",
            "ingress": {
                # TLS (change to whatever ports you need),
                "from_port": 443,
                "to_port": 443,
                "protocol": "-1",
                "cidr_blocks": ['0.0.0.0/0'],
            },

            "egress": {
                "from_port": 0,
                "to_port": 0,
                "protocol": "-1",
                "cidr_blocks": ["0.0.0.0/0"],
                "prefix_list_ids": ["pl-12c4e678"],
            }
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
