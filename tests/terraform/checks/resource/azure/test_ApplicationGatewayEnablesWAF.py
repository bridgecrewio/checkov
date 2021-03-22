import unittest

import hcl2

from checkov.terraform.checks.resource.azure.ApplicationGatewayEnablesWAF import check
from checkov.common.models.enums import CheckResult


class TestApplicationGatewayEnablesWAF(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_application_gateway" "network" {
              name                = "example-appgateway"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location
            
              sku {
                name     = "Standard_Small"
                tier     = "Standard"
                capacity = 2
              }
            
              gateway_ip_configuration {
                name      = "my-gateway-ip-configuration"
                subnet_id = azurerm_subnet.frontend.id
              }
            
              frontend_port {
                name = local.frontend_port_name
                port = 80
              }
            
              frontend_ip_configuration {
                name                 = local.frontend_ip_configuration_name
                public_ip_address_id = azurerm_public_ip.example.id
              }
            
              backend_address_pool {
                name = local.backend_address_pool_name
              }
            
              backend_http_settings {
                name                  = local.http_setting_name
                cookie_based_affinity = "Disabled"
                path                  = "/path1/"
                port                  = 80
                protocol              = "Http"
                request_timeout       = 60
              }
            
              http_listener {
                name                           = local.listener_name
                frontend_ip_configuration_name = local.frontend_ip_configuration_name
                frontend_port_name             = local.frontend_port_name
                protocol                       = "Http"
              }
            
              request_routing_rule {
                name                       = local.request_routing_rule_name
                rule_type                  = "Basic"
                http_listener_name         = local.listener_name
                backend_address_pool_name  = local.backend_address_pool_name
                backend_http_settings_name = local.http_setting_name
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_application_gateway']['network']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_application_gateway" "network" {
              name                = "example-appgateway"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location
              waf_configuration {
                enabled = false
              }
              sku {
                name     = "Standard_Small"
                tier     = "Standard"
                capacity = 2
              }
            
              gateway_ip_configuration {
                name      = "my-gateway-ip-configuration"
                subnet_id = azurerm_subnet.frontend.id
              }
            
              frontend_port {
                name = local.frontend_port_name
                port = 80
              }
            
              frontend_ip_configuration {
                name                 = local.frontend_ip_configuration_name
                public_ip_address_id = azurerm_public_ip.example.id
              }
            
              backend_address_pool {
                name = local.backend_address_pool_name
              }
            
              backend_http_settings {
                name                  = local.http_setting_name
                cookie_based_affinity = "Disabled"
                path                  = "/path1/"
                port                  = 80
                protocol              = "Http"
                request_timeout       = 60
              }
            
              http_listener {
                name                           = local.listener_name
                frontend_ip_configuration_name = local.frontend_ip_configuration_name
                frontend_port_name             = local.frontend_port_name
                protocol                       = "Http"
              }
            
              request_routing_rule {
                name                       = local.request_routing_rule_name
                rule_type                  = "Basic"
                http_listener_name         = local.listener_name
                backend_address_pool_name  = local.backend_address_pool_name
                backend_http_settings_name = local.http_setting_name
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_application_gateway']['network']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_application_gateway" "network" {
              name                = "example-appgateway"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location
              waf_configuration {
                enabled = true
              }
              sku {
                name     = "Standard_Small"
                tier     = "Standard"
                capacity = 2
              }
            
              gateway_ip_configuration {
                name      = "my-gateway-ip-configuration"
                subnet_id = azurerm_subnet.frontend.id
              }
            
              frontend_port {
                name = local.frontend_port_name
                port = 80
              }
            
              frontend_ip_configuration {
                name                 = local.frontend_ip_configuration_name
                public_ip_address_id = azurerm_public_ip.example.id
              }
            
              backend_address_pool {
                name = local.backend_address_pool_name
              }
            
              backend_http_settings {
                name                  = local.http_setting_name
                cookie_based_affinity = "Disabled"
                path                  = "/path1/"
                port                  = 80
                protocol              = "Http"
                request_timeout       = 60
              }
            
              http_listener {
                name                           = local.listener_name
                frontend_ip_configuration_name = local.frontend_ip_configuration_name
                frontend_port_name             = local.frontend_port_name
                protocol                       = "Http"
              }
            
              request_routing_rule {
                name                       = local.request_routing_rule_name
                rule_type                  = "Basic"
                http_listener_name         = local.listener_name
                backend_address_pool_name  = local.backend_address_pool_name
                backend_http_settings_name = local.http_setting_name
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_application_gateway']['network']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
