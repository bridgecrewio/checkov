import unittest

import hcl2

from checkov.terraform.checks.resource.azure.SecurityCenterContactEmailAlert import check
from checkov.common.models.enums import CheckResult


class TestSecurityCenterEmailAlert(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_security_center_contact" "example" {
              email = "contact@example.com"
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_security_center_contact']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_security_center_contact" "example" {
              email = "contact@example.com"
              phone = "+1-555-555-5555"
              alert_notifications = true
              alerts_to_admins    = true
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_security_center_contact']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
