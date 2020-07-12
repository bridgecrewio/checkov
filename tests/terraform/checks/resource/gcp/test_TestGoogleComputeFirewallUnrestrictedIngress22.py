import unittest
import hcl2

from checkov.terraform.checks.resource.gcp.GoogleComputeFirewallUnrestrictedIngress22 import check, PORT
from checkov.common.models.enums import CheckResult


class TestGoogleComputeFirewallUnrestrictedIngress22(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
resource "google_compute_firewall" "allow_all" {
  name = "terragoat-${var.environment}-firewall"
  network = google_compute_network.vpc.id
  source_ranges = ["0.0.0.0/0"]
  allow {
    protocol = "tcp"
    ports = ["0-65535"]
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['google_compute_firewall']['allow_all']

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_int(self):
        hcl_res = hcl2.loads("""
resource "google_compute_firewall" "allow_all" {
  name = "terragoat-${var.environment}-firewall"
  network = google_compute_network.vpc.id
  source_ranges = ["0.0.0.0/0"]
  allow {
    protocol = "tcp"
    ports = [22]
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['google_compute_firewall']['allow_all']

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_specific(self):
            hcl_res = hcl2.loads("""
    resource "google_compute_firewall" "allow_all" {
      name = "terragoat-${var.environment}-firewall"
      network = google_compute_network.vpc.id
      source_ranges = ["0.0.0.0/0"]
      allow {
        protocol = "tcp"
        ports = ["1024-65535", "22"]
      }
    }
            """)
            resource_conf = hcl_res['resource'][0]['google_compute_firewall']['allow_all']

            scan_result = check.scan_resource_conf(conf=resource_conf)
            self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['${var.name}-${var.region}-mesos-ssh'],
                         'network': ['${google_compute_network.mesos-global-net.name}'],
                         'allow': [{'protocol': ['tcp'], 'ports': [[
                             str(PORT)]]}], 'target_tags': [['ssh']], 'source_ranges': [['172.1.2.3/32']]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_unknown(self):
        conf = {'count': ['${length(var.firewall_networks)}'], 'project': ['${length(var.firewall_networks) == 1 && var.firewall_projects[0] == "default" ? var.project : var.firewall_projects[count.index]}'], 'name': ['${var.name}-hc-${count.index}'], 'network': ['${var.firewall_networks[count.index]}'], 'source_ranges': [['130.211.0.0/22', '35.191.0.0/16']], 'target_tags': ['${length(var.target_tags) > 0 ? var.target_tags : None}'], 'target_service_accounts': ['${length(var.target_service_accounts) > 0 ? var.target_service_accounts : None}'], 'dynamic': [{'allow': {'for_each': ['${var.backends}'], 'content': [{'protocol': ['tcp'], 'ports': [['${allow.value.port}']]}]}}], 'allow': ['${var.backends}']}
        scan_result = check.scan_resource_conf(conf)
        self.assertEqual(scan_result, CheckResult.UNKNOWN)

    def test_success_int(self):
        hcl_res = hcl2.loads("""
resource "google_compute_firewall" "allow_all" {
  name = "terragoat-${var.environment}-firewall"
  network = google_compute_network.vpc.id
  source_ranges = ["0.0.0.0/0"]
  allow {
    protocol = "tcp"
    ports = [4624]
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['google_compute_firewall']['allow_all']

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
