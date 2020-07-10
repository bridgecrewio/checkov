import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleComputeFirewallUnrestrictedIngress3389 import check, PORT
from checkov.common.models.enums import CheckResult


class TestGoogleComputeFirewallUnrestrictedIngress3389(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['${var.name}-${var.region}-mesos-ssh'],
                         'network': ['${google_compute_network.mesos-global-net.name}'],
                         'allow': [{'protocol': ['tcp'], 'ports': [[str(PORT)]]}], 'target_tags': [['ssh']],
                         'source_ranges': [['0.0.0.0/0']]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_1(self):
        resource_conf = {'name': ['${var.name}-${var.region}-mesos-ssh'],
                         'network': ['${google_compute_network.mesos-global-net.name}'],
                         'allow': [{'protocol': ['tcp'], 'ports': [[
                             str(PORT)]]}], 'target_tags': [['ssh']], 'source_ranges': [['172.1.2.3/32']]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_2(self):
        hcl_res = hcl2.loads("""
                    resource "google_compute_firewall" "no-allow-blocks" {
                      name        = "deny-all-egress-all"
                      description = "Prevent all egress traffic by default"
                      disabled = true
                    
                      network        = google_compute_network.vpc_network.name
                      enable_logging = true
                    
                      priority           = 65534
                      direction          = "EGRESS"
                      destination_ranges = ["0.0.0.0/0"]
                      deny { protocol = "all" }
                    }
                        """)
        resource_conf = hcl_res['resource'][0]['google_compute_firewall']['no-allow-blocks']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
