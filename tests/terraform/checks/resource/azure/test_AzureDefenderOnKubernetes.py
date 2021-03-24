import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AzureDefenderOnKubernetes import check
from checkov.common.models.enums import CheckResult


class TestAzureDefenderOnKubernetes(unittest.TestCase):

    def test_failure1(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_security_center_subscription_pricing" "example" {
                  tier          = "Free"
                  resource_type = "KubernetesService"
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_security_center_subscription_pricing']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_security_center_subscription_pricing" "example" {
                  tier          = "Standard"
                  resource_type = "KubernetesService"
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_security_center_subscription_pricing']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
