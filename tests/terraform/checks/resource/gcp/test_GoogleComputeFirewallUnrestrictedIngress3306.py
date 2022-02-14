import unittest
import hcl2

from checkov.terraform.checks.resource.gcp.GoogleComputeFirewallUnrestrictedIngress3306 import check, PORT
from checkov.common.models.enums import CheckResult


class TestGoogleComputeFirewallUnrestrictedIngress3306(unittest.TestCase):

    def test_failure(self):
        resource_conf = {
            'name': ['mysql-database-public'],
            'network': ['${google_compute_network.mysql-network.name}'],
            'allow': [
                {
                    'protocol': ['tcp'],
                    'ports': [[str(PORT)]]
                }
            ],
            'source_ranges': [['0.0.0.0/0']]
            }

        # This fails because we are allowing unrestricted mysql access
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_1(self):
        resource_conf = {
            'name': ['mysql-database-public'],
            'network': ['${google_compute_network.mysql-network.name}'],
            'allow': [
                {
                    'protocol': ['tcp'],
                    'ports': [[str(PORT)]]
                }
            ],
            'source_ranges': [['172.1.2.3/32']]  # Non-public CIDR
            }

        # This passes b/c we specify a non-public CIDR/IP
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_2(self):
        hcl_res = hcl2.loads(
            """
                resource "google_compute_firewall" "deny-all-egress" {
                    name        = "deny-all-egress"
                    description = "Prevent all egress traffic by default"

                    network        = google_compute_network.vpc_network.name
                    enable_logging = true

                    priority           = 65534
                    direction          = "EGRESS"
                    destination_ranges = ["0.0.0.0/0"]
                    deny { protocol = "all" }
                }
            """
            )
        resource_conf = hcl_res['resource'][0]['google_compute_firewall']['deny-all-egress']

        # This passes b/c we always pass if "allow" is not found
        # We tested "deny { protocol = "all" }" so there is no "allow" rule
        # Check AbsGoogleComputeFirewallUnrestrictedIngress.py file for logic
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
