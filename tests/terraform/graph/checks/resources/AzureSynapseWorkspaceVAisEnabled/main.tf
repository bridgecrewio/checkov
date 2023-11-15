variable "default_var" {
  default = "pud-default"
}

# Case 1: Pass: Connection exists and recurring_scans.*.enabled = true

resource "azurerm_synapse_workspace" "synapse_ws_pass_1" {
  name                                 = "synapse_ws_pass_1"
  resource_group_name                  = var.default_var
  location                             = var.default_var
  storage_data_lake_gen2_filesystem_id = var.default_var
  sql_administrator_login              = "pudsqladminuser"
  sql_administrator_login_password     = "P@ssw0rd@1" # checkov:skip=CKV_SECRET_80 test secret

  aad_admin {
    login     = "AzureAD Admin"
    object_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "00000000-0000-0000-0000-000000000000"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Env = "production"
  }
}

resource "azurerm_synapse_workspace_security_alert_policy" "synapse_ws_policy_1" {
  synapse_workspace_id       = azurerm_synapse_workspace.synapse_ws_pass_1.id
  policy_state               = "Enabled"

  disabled_alerts = [
    "Sql_Injection",
    "Data_Exfiltration"
  ]
  retention_days = 20
}

resource "azurerm_synapse_workspace_vulnerability_assessment" "va_pass" {
  workspace_security_alert_policy_id = azurerm_synapse_workspace_security_alert_policy.synapse_ws_policy_1.id
  storage_container_path             = var.default_var

  recurring_scans {
    enabled = true
  }
}

# Case 2: Fail: Connection doesn't exist but recurring_scans.*.enabled = true

resource "azurerm_synapse_workspace" "synapse_ws_fail_1" {
  name                                 = "synapse_ws_fail_1"
  resource_group_name                  = var.default_var
  location                             = var.default_var
  storage_data_lake_gen2_filesystem_id = var.default_var
  sql_administrator_login              = "pudsqladminuser"
  sql_administrator_login_password     = "P@ssw0rd@1" # checkov:skip=CKV_SECRET_80 test secret

  aad_admin {
    login     = "AzureAD Admin"
    object_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "00000000-0000-0000-0000-000000000000"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Env = "production"
  }
}

resource "azurerm_synapse_workspace_security_alert_policy" "synapse_ws_policy_2" {
  synapse_workspace_id       = azurerm_synapse_workspace.synapse_ws_fail_1.id
  policy_state               = "Enabled"

  disabled_alerts = [
    "Sql_Injection",
    "Data_Exfiltration"
  ]
  retention_days = 20
}

resource "azurerm_synapse_workspace_vulnerability_assessment" "va_fail_1" {
  workspace_security_alert_policy_id = var.default_var
  storage_container_path             = var.default_var

  recurring_scans {
    enabled = true
  }
}

# Case 3: Fail: Connection exists but recurring_scans.*.enabled = false

resource "azurerm_synapse_workspace" "synapse_ws_fail_2" {
  name                                 = "synapse_ws_fail_2"
  resource_group_name                  = var.default_var
  location                             = var.default_var
  storage_data_lake_gen2_filesystem_id = var.default_var
  sql_administrator_login              = "pudsqladminuser"
  sql_administrator_login_password     = "P@ssw0rd@1" # checkov:skip=CKV_SECRET_80 test secret

  aad_admin {
    login     = "AzureAD Admin"
    object_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "00000000-0000-0000-0000-000000000000"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Env = "production"
  }
}

resource "azurerm_synapse_workspace_security_alert_policy" "synapse_ws_policy_3" {
  synapse_workspace_id       = azurerm_synapse_workspace.synapse_ws_fail_2.id
  policy_state               = "Enabled"

  disabled_alerts = [
    "Sql_Injection",
    "Data_Exfiltration"
  ]
  retention_days = 20
}

resource "azurerm_synapse_workspace_vulnerability_assessment" "va_fail_2" {
  workspace_security_alert_policy_id = azurerm_synapse_workspace_security_alert_policy.synapse_ws_policy_3.id
  storage_container_path             = var.default_var

  recurring_scans {
    enabled = false
  }
}


# Case 4: Fail: 'azurerm_synapse_workspace_security_alert_policy' not connected to 'azurerm_synapse_workspace' but recurring_scans.*.enabled = true

resource "azurerm_synapse_workspace" "synapse_ws_fail_3" {
  name                                 = "synapse_ws_fail_3"
  resource_group_name                  = var.default_var
  location                             = var.default_var
  storage_data_lake_gen2_filesystem_id = var.default_var
  sql_administrator_login              = "pudsqladminuser"
  sql_administrator_login_password     = "P@ssw0rd@1" # checkov:skip=CKV_SECRET_80 test secret

  aad_admin {
    login     = "AzureAD Admin"
    object_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "00000000-0000-0000-0000-000000000000"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Env = "production"
  }
}

resource "azurerm_synapse_workspace_security_alert_policy" "synapse_ws_policy_4" {
  synapse_workspace_id       = var.default_var
  policy_state               = "Enabled"

  disabled_alerts = [
    "Sql_Injection",
    "Data_Exfiltration"
  ]
  retention_days = 20
}

resource "azurerm_synapse_workspace_vulnerability_assessment" "va_fail_3" {
  workspace_security_alert_policy_id = azurerm_synapse_workspace_security_alert_policy.synapse_ws_policy_4.id
  storage_container_path             = var.default_var

  recurring_scans {
    enabled = true
  }
}