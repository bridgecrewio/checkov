import unittest

from checkov.terraform.checks.resource.gcp.GKEAliasIpEnabled import check
from checkov.common.models.enums import CheckResult
import hcl2


resource_conf = '''
resource "google_container_cluster" "fail" {
  name                     = "fail-cluster"
}

resource "google_container_cluster" "success" {
  name                     = "success-cluster"
  ip_allocation_policy {}
}
'''


class TestGKEAliasIpEnabled(unittest.TestCase):

    def test_failure(self):
        resource = hcl2.loads(resource_conf)[
            'resource'][0]['google_container_cluster']['fail']
        scan_result = check.scan_resource_conf(conf=resource)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource = hcl2.loads(resource_conf)[
            'resource'][1]['google_container_cluster']['success']

        scan_result = check.scan_resource_conf(
            conf=resource)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
