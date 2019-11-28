import unittest

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.resource_scanners.aws.SecurityGroupUnrestrictedIngress3389 import scanner


class TestSecurityGroupUnrestrictedIngress3389(unittest.TestCase):

    def test_failure(self):
        resource_conf = {
            "name": "allow_rdp",
            "description": "Allow RDP inbound traffic",
            "vpc_id": "${aws_vpc.main.id}",
            "ingress": {
                # TLS (change to whatever ports you need),
                "from_port": 3389,
                "to_port": 3389,
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
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

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
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
