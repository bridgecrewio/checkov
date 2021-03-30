import unittest

import hcl2

from checkov.terraform.checks.resource.azure.RedisCacheEnableNonSSLPort import check
from checkov.common.models.enums import CheckResult


class TestRedisCacheEnableNonSSLPort(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                    resource "azurerm_redis_cache" "example" {
                      name                = "example-cache"
                      location            = azurerm_resource_group.example.location
                      resource_group_name = azurerm_resource_group.example.name
                      capacity            = 2
                      family              = "C"
                      sku_name            = "Standard"
                      enable_non_ssl_port = true
                      minimum_tls_version = "1.2"
                      public_network_access_enabled  = true
                      redis_configuration {
                      }
                    }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_redis_cache']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                    resource "azurerm_redis_cache" "example" {
                      name                = "example-cache"
                      location            = azurerm_resource_group.example.location
                      resource_group_name = azurerm_resource_group.example.name
                      capacity            = 2
                      family              = "C"
                      sku_name            = "Standard"
                      enable_non_ssl_port = false
                      minimum_tls_version = "1.2"
                      public_network_access_enabled  = true

                      redis_configuration {
                      }
                    }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_redis_cache']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_no_param(self):
        hcl_res = hcl2.loads("""
                    resource "azurerm_redis_cache" "example" {
                      name                = "example-cache"
                      location            = azurerm_resource_group.example.location
                      resource_group_name = azurerm_resource_group.example.name
                      capacity            = 2
                      family              = "C"
                      sku_name            = "Standard"
                      minimum_tls_version = "1.2"

                      redis_configuration {
                      }
                    }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_redis_cache']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
