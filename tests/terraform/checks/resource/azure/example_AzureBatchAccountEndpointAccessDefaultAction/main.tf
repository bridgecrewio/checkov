#pass
resource "azurerm_batch_account" "pass_no_publicNetworkAccess" {
  name                                = "testbatchaccount"
  resource_group_name                 = "group"
  location                            = "azurerm_resource_group.example.location"
  pool_allocation_mode                = "BatchService"
}

resource "azurerm_batch_account" "pass_publicNetworkAccess_disabled" {
  name                                = "testbatchaccount"
  resource_group_name                 = "group"
  location                            = "azurerm_resource_group.example.location"
  pool_allocation_mode                = "BatchService"
  public_network_access_enabled       = false
}

resource "azurerm_batch_account" "pass_publicNetworkAccess_enabled_no_network_profile" {
  name                                = "testbatchaccount"
  resource_group_name                 = "group"
  location                            = "azurerm_resource_group.example.location"
  pool_allocation_mode                = "BatchService"
  public_network_access_enabled       = true
}

resource "azurerm_batch_account" "pass_publicNetworkAccess_enabled_no_account_access" {
  name                                = "testbatchaccount"
  resource_group_name                 = "group"
  location                            = "azurerm_resource_group.example.location"
  pool_allocation_mode                = "BatchService"
  public_network_access_enabled       = true
  network_profile {

  }
}

resource "azurerm_batch_account" "pass_publicNetworkAccess_enabled_default_action_deny" {
  name                                = "testbatchaccount"
  resource_group_name                 = "group"
  location                            = "azurerm_resource_group.example.location"
  pool_allocation_mode                = "BatchService"
  public_network_access_enabled       = true
  network_profile {
    account_access {
      default_action = "deny"
    }
  }
}

resource "azurerm_batch_account" "fail_publicNetworkAccess_enabled_default_action_allow" {
  name                                = "testbatchaccount"
  resource_group_name                 = "group"
  location                            = "azurerm_resource_group.example.location"
  pool_allocation_mode                = "BatchService"
  public_network_access_enabled       = true
  network_profile {
    account_access {
      default_action = "allow"
    }
  }
}