import unittest

import hcl2

from checkov.terraform.checks.resource.azure.APIServicesUseVirtualNetwork import check
from checkov.common.models.enums import CheckResult


class TestAPIServicesUseVirtualNetwork(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_api_management" "example" {
                  name                = "example-apim"
                  location            = azurerm_resource_group.example.location
                  resource_group_name = azurerm_resource_group.example.name
                  publisher_name      = "My Company"
                  publisher_email     = "company@terraform.io"
                
                  sku_name = "Developer_1"
                
                  policy {
                    xml_content = <<XML
                    <policies>
                      <inbound />
                      <backend />
                      <outbound />
                      <on-error />
                    </policies>
                XML
                
                  }
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_api_management']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_api_management" "example" {
                  name                = "example-apim"
                  location            = azurerm_resource_group.example.location
                  resource_group_name = azurerm_resource_group.example.name
                  publisher_name      = "My Company"
                  publisher_email     = "company@terraform.io"
                
                  sku_name = "Developer_1"
                  virtual_network_configuration {
                    subnet_id = azure_subnet.subnet_not_public_ip.id
                  }
                  policy {
                    xml_content = <<XML
                    <policies>
                      <inbound />
                      <backend />
                      <outbound />
                      <on-error />
                    </policies>
                XML
                
                  }
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_api_management']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
