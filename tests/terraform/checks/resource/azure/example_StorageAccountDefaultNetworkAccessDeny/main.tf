#not set - ignore
            resource "azurerm_storage_account" "unknown" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
            }
# deny so pass
resource "azurerm_storage_account" "pass" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              network_rules {
                default_action             = "Deny"
                ip_rules                   = ["100.0.0.1"]
                virtual_network_subnet_ids = [azurerm_subnet.example.id]
              }
            }
#allow so fail
            resource "azurerm_storage_account" "fail" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              network_rules {
                default_action             = "Allow"
                ip_rules                   = ["100.0.0.1"]
                virtual_network_subnet_ids = [azurerm_subnet.example.id]
              }
            }

#allow fail
            resource "azurerm_storage_account_network_rules" "fail" {
              resource_group_name  = azurerm_resource_group.test.name
              storage_account_name = azurerm_storage_account.test.name

              default_action             = "Allow"
              ip_rules                   = ["127.0.0.1"]
              virtual_network_subnet_ids = [azurerm_subnet.test.id]
              bypass                     = ["Metrics"]
              storage_account_id         = ""
            }
#deny so pass
            resource "azurerm_storage_account_network_rules" "pass" {
              resource_group_name  = azurerm_resource_group.test.name
              storage_account_name = azurerm_storage_account.test.name

              default_action             = "Deny"
              ip_rules                   = ["127.0.0.1"]
              virtual_network_subnet_ids = [azurerm_subnet.test.id]
              bypass                     = ["Metrics"]
              storage_account_id         = ""
            }

