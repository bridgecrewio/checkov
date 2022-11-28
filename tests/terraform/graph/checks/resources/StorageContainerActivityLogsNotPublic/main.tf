# -------------------------------------------------------------------- #
# default in azurerm_monitor_activity_log_alert is logging enabled
resource "azurerm_storage_container" "ok_container_log_enabled_by_default" {
  name                  = "vhds"
  storage_account_name  = azurerm_storage_account.ok_account_1.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "ok_container_log_enabled_by_default_2" {
  name                  = "vhds"
  storage_account_name  = azurerm_storage_account.ok_account_1.name
}

resource "azurerm_storage_container" "not_ok_container_log_enabled_by_default" {
  name                  = "vhds"
  storage_account_name  = azurerm_storage_account.ok_account_1.name
  container_access_type = "blob"
}

resource "azurerm_storage_account" "ok_account_1" {
  name                     = "examplesa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_monitor_activity_log_alert" "ok_monitor_activity_log_alert_1" {
  name                = "example-activitylogalert"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_resource_group.main.id]
  description         = "This alert will monitor a specific storage account updates."

  criteria {
    resource_id    = azurerm_storage_account.ok_account_1.id
    operation_name = "Microsoft.Storage/storageAccounts/write"
    category       = "Recommendation"
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id

    webhook_properties = {
      from = "terraform"
    }
  }
}

# -------------------------------------------------------------------- #
# if log is enabled explicitly
resource "azurerm_storage_container" "ok_container_log_enabled" {
  name                  = "vhds"
  storage_account_name  = azurerm_storage_account.ok_account_2.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "ok_container_log_enabled_2" {
  name                  = "vhds"
  storage_account_name  = azurerm_storage_account.ok_account_2.name
}

resource "azurerm_storage_container" "not_ok_container_log_enabled" {
  name                  = "vhds"
  storage_account_name  = azurerm_storage_account.ok_account_2.name
  container_access_type = "blob"
}

resource "azurerm_storage_account" "ok_account_2" {
  name                     = "examplesa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_monitor_activity_log_alert" "ok_monitor_activity_log_alert_2" {
  name                = "example-activitylogalert"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_resource_group.main.id]
  description         = "This alert will monitor a specific storage account updates."
  enabled             = true

  criteria {
    resource_id    = azurerm_storage_account.ok_account_2.id
    operation_name = "Microsoft.Storage/storageAccounts/write"
    category       = "Recommendation"
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id

    webhook_properties = {
      from = "terraform"
    }
  }
}

# -------------------------------------------------------------------- #
# logging disabled - doesn't care if container private or not

resource "azurerm_storage_container" "ok_container_log_disabled_3" {
  name                  = "vhds"
  storage_account_name  = azurerm_storage_account.ok_account_3.name
  container_access_type = "blob"
}

resource "azurerm_storage_container" "ok_container_log_disabled" {
  name                  = "vhds"
  storage_account_name  = azurerm_storage_account.ok_account_3.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "ok_container_log_disabled_2" {
  name                  = "vhds"
  storage_account_name  = azurerm_storage_account.ok_account_3.name
}

resource "azurerm_storage_account" "ok_account_3" {
  name                     = "examplesa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_monitor_activity_log_alert" "not_enabled_monitor_activity_log_alert" {
  name                = "example-activitylogalert"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_resource_group.main.id]
  description         = "This alert will monitor a specific storage account updates."
  enabled             = false

  criteria {
    resource_id    = azurerm_storage_account.ok_account_3.id
    operation_name = "Microsoft.Storage/storageAccounts/write"
    category       = "Recommendation"
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id

    webhook_properties = {
      from = "terraform"
    }
  }
}

# -------------------------------------------------------------------- #
# container with no connection to logging at all - all good

resource "azurerm_storage_container" "ok_container_4" {
  name                  = "vhds"
  storage_account_name  = azurerm_storage_account.ok_account_4.name
  container_access_type = "blob"
}

resource "azurerm_storage_account" "ok_account_4" {
  name                     = "examplesa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

# -------------------------------------------------------------------- #
# other resources
resource "azurerm_resource_group" "main" {
  name     = "okLegacyExample-resources"
  location = "West Europe"
}

resource "azurerm_monitor_action_group" "main" {
  name                = "CriticalAlertsAction"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "p0action"
}