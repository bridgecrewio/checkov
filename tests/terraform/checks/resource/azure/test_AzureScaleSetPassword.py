import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AzureScaleSetPassword import check
from checkov.common.models.enums import CheckResult


class TestAzureScaleSetPassword(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_linux_virtual_machine_scale_set" "example" {
            name                = var.scaleset_name
            resource_group_name = var.resource_group.name
            location            = var.resource_group.location
            sku                 = var.sku
            instances           = var.instance_count
            admin_username      = var.admin_username
            disable_password_authentication = false
            tags = var.common_tags
        }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_linux_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_linux_virtual_machine_scale_set" "example" {
            name                = var.scaleset_name
            resource_group_name = var.resource_group.name
            location            = var.resource_group.location
            sku                 = var.sku
            instances           = var.instance_count
            admin_username      = var.admin_username
            disable_password_authentication = true

                admin_ssh_key {
                    username   = var.admin_username
                    public_key = tls_private_key.new.public_key_pem
                }
            tags = var.common_tags
        }
                        """)
        resource_conf = hcl_res['resource'][0]['azurerm_linux_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
