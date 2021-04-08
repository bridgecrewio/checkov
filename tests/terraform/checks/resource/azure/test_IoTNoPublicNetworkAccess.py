import unittest

import hcl2

from checkov.terraform.checks.resource.azure.IoTNoPublicNetworkAccess import check
from checkov.common.models.enums import CheckResult


class TestIoTNoPublicNetworkAccess(unittest.TestCase):

    def test_success_missing_attribute(self):
        hcl_res = hcl2.loads("""
           resource "azurerm_iothub" "example" {
              name                = "Example-IoTHub"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location
            
              sku {
                name     = "S1"
                capacity = "1"
              }
            
              endpoint {
                type                       = "AzureIotHub.StorageContainer"
                connection_string          = azurerm_storage_account.example.primary_blob_connection_string
                name                       = "export"
                batch_frequency_in_seconds = 60
                max_chunk_size_in_bytes    = 10485760
                container_name             = azurerm_storage_container.example.name
                encoding                   = "Avro"
                file_name_format           = "{iothub}/{partition}_{YYYY}_{MM}_{DD}_{HH}_{mm}"
              }
            
              endpoint {
                type              = "AzureIotHub.EventHub"
                connection_string = azurerm_eventhub_authorization_rule.example.primary_connection_string
                name              = "export2"
              }
            
              route {
                name           = "export"
                source         = "DeviceMessages"
                condition      = "true"
                endpoint_names = ["export"]
                enabled        = true
              }
            
              route {
                name           = "export2"
                source         = "DeviceMessages"
                condition      = "true"
                endpoint_names = ["export2"]
                enabled        = true
              }
            
              enrichment {
                key            = "tenant"
                value          = "$twin.tags.Tenant"
                endpoint_names = ["export", "export2"]
              }
            
              tags = {
                purpose = "testing"
              }
            }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_iothub']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads("""
           resource "azurerm_iothub" "example" {
              name                = "Example-IoTHub"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location
            
              sku {
                name     = "S1"
                capacity = "1"
              }
            
              endpoint {
                type                       = "AzureIotHub.StorageContainer"
                connection_string          = azurerm_storage_account.example.primary_blob_connection_string
                name                       = "export"
                batch_frequency_in_seconds = 60
                max_chunk_size_in_bytes    = 10485760
                container_name             = azurerm_storage_container.example.name
                encoding                   = "Avro"
                file_name_format           = "{iothub}/{partition}_{YYYY}_{MM}_{DD}_{HH}_{mm}"
              }
            
              endpoint {
                type              = "AzureIotHub.EventHub"
                connection_string = azurerm_eventhub_authorization_rule.example.primary_connection_string
                name              = "export2"
              }
              public_network_access_enabled = true
              route {
                name           = "export"
                source         = "DeviceMessages"
                condition      = "true"
                endpoint_names = ["export"]
                enabled        = true
              }
            
              route {
                name           = "export2"
                source         = "DeviceMessages"
                condition      = "true"
                endpoint_names = ["export2"]
                enabled        = true
              }
            
              enrichment {
                key            = "tenant"
                value          = "$twin.tags.Tenant"
                endpoint_names = ["export", "export2"]
              }
            
              tags = {
                purpose = "testing"
              }
            }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_iothub']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_iothub" "example" {
              name                = "Example-IoTHub"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location
            
              sku {
                name     = "S1"
                capacity = "1"
              }
            
              endpoint {
                type                       = "AzureIotHub.StorageContainer"
                connection_string          = azurerm_storage_account.example.primary_blob_connection_string
                name                       = "export"
                batch_frequency_in_seconds = 60
                max_chunk_size_in_bytes    = 10485760
                container_name             = azurerm_storage_container.example.name
                encoding                   = "Avro"
                file_name_format           = "{iothub}/{partition}_{YYYY}_{MM}_{DD}_{HH}_{mm}"
              }
            
              endpoint {
                type              = "AzureIotHub.EventHub"
                connection_string = azurerm_eventhub_authorization_rule.example.primary_connection_string
                name              = "export2"
              }
            
              route {
                name           = "export"
                source         = "DeviceMessages"
                condition      = "true"
                endpoint_names = ["export"]
                enabled        = true
              }
            
              route {
                name           = "export2"
                source         = "DeviceMessages"
                condition      = "true"
                endpoint_names = ["export2"]
                enabled        = true
              }
            
              enrichment {
                key            = "tenant"
                value          = "$twin.tags.Tenant"
                endpoint_names = ["export", "export2"]
              }
              public_network_access_enabled = false
              tags = {
                purpose = "testing"
              }
            }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_iothub']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
