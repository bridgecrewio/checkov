import unittest

from checkov.terraform.checks.resource.azure.AzureInstancePassword import check
from checkov.common.models.enums import CheckResult


class TestAzureInstancePassword(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "name": ["${var.prefix}-vm"],
            "location": ["${azurerm_resource_group.main.location}"],
            "resource_group_name": ["${azurerm_resource_group.main.name}"],
            "network_interface_ids": [["${azurerm_network_interface.main.id}"]],
            "vm_size": ["Standard_DS1_v2"],
            "storage_image_reference": [
                {"publisher": ["Canonical"], "offer": ["UbuntuServer"], "sku": ["16.04-LTS"], "version": ["latest"]}
            ],
            "storage_os_disk": [
                {
                    "name": ["myosdisk1"],
                    "caching": ["ReadWrite"],
                    "create_option": ["FromImage"],
                    "managed_disk_type": ["Standard_LRS"],
                }
            ],
            "os_profile": [
                {"computer_name": ["hostname"], "admin_username": ["testadmin"], "admin_password": ["Password1234!"]}
            ],
            "os_profile_linux_config": [{"disable_password_authentication": [False]}],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": ["${var.prefix}-vm"],
            "location": ["${azurerm_resource_group.main.location}"],
            "resource_group_name": ["${azurerm_resource_group.main.name}"],
            "network_interface_ids": [["${azurerm_network_interface.main.id}"]],
            "vm_size": ["Standard_DS1_v2"],
            "storage_image_reference": [
                {"publisher": ["Canonical"], "offer": ["UbuntuServer"], "sku": ["16.04-LTS"], "version": ["latest"]}
            ],
            "storage_os_disk": [
                {
                    "name": ["myosdisk1"],
                    "caching": ["ReadWrite"],
                    "create_option": ["FromImage"],
                    "managed_disk_type": ["Standard_LRS"],
                }
            ],
            "os_profile": [
                {"computer_name": ["hostname"], "admin_username": ["testadmin"], "admin_password": ["Password1234!"]}
            ],
            "os_profile_linux_config": [{"disable_password_authentication": [True]}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
