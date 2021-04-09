import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.VMScaleSetsAutoOSImagePatchingEnabled import check


class TestVMScaleSetsAutoOSImagePatchingEnabled(unittest.TestCase):

    def test_failure1(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_virtual_machine_scale_set" "example" {
          name                = "mytestscaleset-1"
          location            = azurerm_resource_group.example.location
          resource_group_name = azurerm_resource_group.example.name
        
          # automatic rolling upgrade
          upgrade_policy_mode  = "Rolling"
        
          rolling_upgrade_policy {
            max_batch_instance_percent              = 20
            max_unhealthy_instance_percent          = 20
            max_unhealthy_upgraded_instance_percent = 5
            pause_time_between_batches              = "PT0S"
          }
        
          # required when using rolling upgrade policy
          health_probe_id = azurerm_lb_probe.example.id
        
          sku {
            name     = "Standard_F2"
            tier     = "Standard"
            capacity = 2
          }
        
          storage_profile_image_reference {
            publisher = "Canonical"
            offer     = "UbuntuServer"
            sku       = "16.04-LTS"
            version   = "latest"
          }
        
          storage_profile_os_disk {
            name              = ""
            caching           = "ReadWrite"
            create_option     = "FromImage"
            managed_disk_type = "Standard_LRS"
          }
        
          storage_profile_data_disk {
            lun           = 0
            caching       = "ReadWrite"
            create_option = "Empty"
            disk_size_gb  = 10
          }
        
          os_profile {
            computer_name_prefix = "testvm"
            admin_username       = "myadmin"
          }
        
          os_profile_linux_config {
            disable_password_authentication = true
        
            ssh_keys {
              path     = "/home/myadmin/.ssh/authorized_keys"
              key_data = file("~/.ssh/demo_key.pub")
            }
          }
        
          network_profile {
            name    = "terraformnetworkprofile"
            primary = true
        
            ip_configuration {
              name                                   = "TestIPConfiguration"
              primary                                = true
              subnet_id                              = azurerm_subnet.example.id
              load_balancer_backend_address_pool_ids = [azurerm_lb_backend_address_pool.bpepool.id]
              load_balancer_inbound_nat_rules_ids    = [azurerm_lb_nat_pool.lbnatpool.id]
            }
          }
        
          tags = {
            environment = "staging"
          }
        }

                """)
        resource_conf = hcl_res['resource'][0]['azurerm_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_virtual_machine_scale_set" "example" {
          name                = "mytestscaleset-1"
          location            = azurerm_resource_group.example.location
          resource_group_name = azurerm_resource_group.example.name

          # automatic rolling upgrade
          automatic_os_upgrade = false
          upgrade_policy_mode  = "Rolling"

          rolling_upgrade_policy {
            max_batch_instance_percent              = 20
            max_unhealthy_instance_percent          = 20
            max_unhealthy_upgraded_instance_percent = 5
            pause_time_between_batches              = "PT0S"
          }

          # required when using rolling upgrade policy
          health_probe_id = azurerm_lb_probe.example.id

          sku {
            name     = "Standard_F2"
            tier     = "Standard"
            capacity = 2
          }

          storage_profile_image_reference {
            publisher = "Canonical"
            offer     = "UbuntuServer"
            sku       = "16.04-LTS"
            version   = "latest"
          }

          storage_profile_os_disk {
            name              = ""
            caching           = "ReadWrite"
            create_option     = "FromImage"
            managed_disk_type = "Standard_LRS"
          }

          storage_profile_data_disk {
            lun           = 0
            caching       = "ReadWrite"
            create_option = "Empty"
            disk_size_gb  = 10
          }

          os_profile {
            computer_name_prefix = "testvm"
            admin_username       = "myadmin"
          }

          os_profile_linux_config {
            disable_password_authentication = true

            ssh_keys {
              path     = "/home/myadmin/.ssh/authorized_keys"
              key_data = file("~/.ssh/demo_key.pub")
            }
          }

          network_profile {
            name    = "terraformnetworkprofile"
            primary = true

            ip_configuration {
              name                                   = "TestIPConfiguration"
              primary                                = true
              subnet_id                              = azurerm_subnet.example.id
              load_balancer_backend_address_pool_ids = [azurerm_lb_backend_address_pool.bpepool.id]
              load_balancer_inbound_nat_rules_ids    = [azurerm_lb_nat_pool.lbnatpool.id]
            }
          }

          tags = {
            environment = "staging"
          }
        }

                """)
        resource_conf = hcl_res['resource'][0]['azurerm_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure3(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_virtual_machine_scale_set" "example" {
          name                = "mytestscaleset-1"
          location            = azurerm_resource_group.example.location
          resource_group_name = azurerm_resource_group.example.name

          # automatic rolling upgrade
          automatic_os_upgrade = true
          upgrade_policy_mode  = "Rolling"

          rolling_upgrade_policy {
            max_batch_instance_percent              = 20
            max_unhealthy_instance_percent          = 20
            max_unhealthy_upgraded_instance_percent = 5
            pause_time_between_batches              = "PT0S"
          }

          # required when using rolling upgrade policy
          health_probe_id = azurerm_lb_probe.example.id

          sku {
            name     = "Standard_F2"
            tier     = "Standard"
            capacity = 2
          }

          storage_profile_image_reference {
            publisher = "Canonical"
            offer     = "UbuntuServer"
            sku       = "16.04-LTS"
            version   = "latest"
          }

          storage_profile_os_disk {
            name              = ""
            caching           = "ReadWrite"
            create_option     = "FromImage"
            managed_disk_type = "Standard_LRS"
          }

          storage_profile_data_disk {
            lun           = 0
            caching       = "ReadWrite"
            create_option = "Empty"
            disk_size_gb  = 10
          }

          os_profile {
            computer_name_prefix = "testvm"
            admin_username       = "myadmin"
          }

          os_profile_linux_config {
            disable_password_authentication = true

            ssh_keys {
              path     = "/home/myadmin/.ssh/authorized_keys"
              key_data = file("~/.ssh/demo_key.pub")
            }
          }

          network_profile {
            name    = "terraformnetworkprofile"
            primary = true

            ip_configuration {
              name                                   = "TestIPConfiguration"
              primary                                = true
              subnet_id                              = azurerm_subnet.example.id
              load_balancer_backend_address_pool_ids = [azurerm_lb_backend_address_pool.bpepool.id]
              load_balancer_inbound_nat_rules_ids    = [azurerm_lb_nat_pool.lbnatpool.id]
            }
          }

          tags = {
            environment = "staging"
          }
        }

                """)
        resource_conf = hcl_res['resource'][0]['azurerm_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure4(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_virtual_machine_scale_set" "example" {
          name                = "mytestscaleset-1"
          location            = azurerm_resource_group.example.location
          resource_group_name = azurerm_resource_group.example.name

          # automatic rolling upgrade
          automatic_os_upgrade = true
          upgrade_policy_mode  = "Rolling"
          
          os_profile_windows_config {
            enable_automatic_upgrades = false
          }

          rolling_upgrade_policy {
            max_batch_instance_percent              = 20
            max_unhealthy_instance_percent          = 20
            max_unhealthy_upgraded_instance_percent = 5
            pause_time_between_batches              = "PT0S"
          }

          # required when using rolling upgrade policy
          health_probe_id = azurerm_lb_probe.example.id

          sku {
            name     = "Standard_F2"
            tier     = "Standard"
            capacity = 2
          }

          storage_profile_image_reference {
            publisher = "Canonical"
            offer     = "UbuntuServer"
            sku       = "16.04-LTS"
            version   = "latest"
          }

          storage_profile_os_disk {
            name              = ""
            caching           = "ReadWrite"
            create_option     = "FromImage"
            managed_disk_type = "Standard_LRS"
          }

          storage_profile_data_disk {
            lun           = 0
            caching       = "ReadWrite"
            create_option = "Empty"
            disk_size_gb  = 10
          }

          os_profile {
            computer_name_prefix = "testvm"
            admin_username       = "myadmin"
          }

          os_profile_linux_config {
            disable_password_authentication = true

            ssh_keys {
              path     = "/home/myadmin/.ssh/authorized_keys"
              key_data = file("~/.ssh/demo_key.pub")
            }
          }

          network_profile {
            name    = "terraformnetworkprofile"
            primary = true

            ip_configuration {
              name                                   = "TestIPConfiguration"
              primary                                = true
              subnet_id                              = azurerm_subnet.example.id
              load_balancer_backend_address_pool_ids = [azurerm_lb_backend_address_pool.bpepool.id]
              load_balancer_inbound_nat_rules_ids    = [azurerm_lb_nat_pool.lbnatpool.id]
            }
          }

          tags = {
            environment = "staging"
          }
        }

                """)
        resource_conf = hcl_res['resource'][0]['azurerm_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure5(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_virtual_machine_scale_set" "example" {
          name                = "mytestscaleset-1"
          location            = azurerm_resource_group.example.location
          resource_group_name = azurerm_resource_group.example.name

          # automatic rolling upgrade
          upgrade_policy_mode  = "Rolling"

          os_profile_windows_config {
            enable_automatic_upgrades = false
          }

          rolling_upgrade_policy {
            max_batch_instance_percent              = 20
            max_unhealthy_instance_percent          = 20
            max_unhealthy_upgraded_instance_percent = 5
            pause_time_between_batches              = "PT0S"
          }

          # required when using rolling upgrade policy
          health_probe_id = azurerm_lb_probe.example.id

          sku {
            name     = "Standard_F2"
            tier     = "Standard"
            capacity = 2
          }

          storage_profile_image_reference {
            publisher = "Canonical"
            offer     = "UbuntuServer"
            sku       = "16.04-LTS"
            version   = "latest"
          }

          storage_profile_os_disk {
            name              = ""
            caching           = "ReadWrite"
            create_option     = "FromImage"
            managed_disk_type = "Standard_LRS"
          }

          storage_profile_data_disk {
            lun           = 0
            caching       = "ReadWrite"
            create_option = "Empty"
            disk_size_gb  = 10
          }

          os_profile {
            computer_name_prefix = "testvm"
            admin_username       = "myadmin"
          }

          os_profile_linux_config {
            disable_password_authentication = true

            ssh_keys {
              path     = "/home/myadmin/.ssh/authorized_keys"
              key_data = file("~/.ssh/demo_key.pub")
            }
          }

          network_profile {
            name    = "terraformnetworkprofile"
            primary = true

            ip_configuration {
              name                                   = "TestIPConfiguration"
              primary                                = true
              subnet_id                              = azurerm_subnet.example.id
              load_balancer_backend_address_pool_ids = [azurerm_lb_backend_address_pool.bpepool.id]
              load_balancer_inbound_nat_rules_ids    = [azurerm_lb_nat_pool.lbnatpool.id]
            }
          }

          tags = {
            environment = "staging"
          }
        }

                """)
        resource_conf = hcl_res['resource'][0]['azurerm_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_virtual_machine_scale_set" "example" {
          name                = "mytestscaleset-1"
          location            = azurerm_resource_group.example.location
          resource_group_name = azurerm_resource_group.example.name

          # automatic rolling upgrade
          automatic_os_upgrade = true
          upgrade_policy_mode  = "Rolling"
          
          os_profile_windows_config {
            enable_automatic_upgrades = true
          }

          rolling_upgrade_policy {
            max_batch_instance_percent              = 20
            max_unhealthy_instance_percent          = 20
            max_unhealthy_upgraded_instance_percent = 5
            pause_time_between_batches              = "PT0S"
          }

          # required when using rolling upgrade policy
          health_probe_id = azurerm_lb_probe.example.id

          sku {
            name     = "Standard_F2"
            tier     = "Standard"
            capacity = 2
          }

          storage_profile_image_reference {
            publisher = "Canonical"
            offer     = "UbuntuServer"
            sku       = "16.04-LTS"
            version   = "latest"
          }

          storage_profile_os_disk {
            name              = ""
            caching           = "ReadWrite"
            create_option     = "FromImage"
            managed_disk_type = "Standard_LRS"
          }

          storage_profile_data_disk {
            lun           = 0
            caching       = "ReadWrite"
            create_option = "Empty"
            disk_size_gb  = 10
          }

          os_profile {
            computer_name_prefix = "testvm"
            admin_username       = "myadmin"
          }

          os_profile_linux_config {
            disable_password_authentication = true

            ssh_keys {
              path     = "/home/myadmin/.ssh/authorized_keys"
              key_data = file("~/.ssh/demo_key.pub")
            }
          }

          network_profile {
            name    = "terraformnetworkprofile"
            primary = true

            ip_configuration {
              name                                   = "TestIPConfiguration"
              primary                                = true
              subnet_id                              = azurerm_subnet.example.id
              load_balancer_backend_address_pool_ids = [azurerm_lb_backend_address_pool.bpepool.id]
              load_balancer_inbound_nat_rules_ids    = [azurerm_lb_nat_pool.lbnatpool.id]
            }
          }

          tags = {
            environment = "staging"
          }
        }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
