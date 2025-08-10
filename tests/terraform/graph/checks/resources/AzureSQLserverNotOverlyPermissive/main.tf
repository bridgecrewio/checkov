# PASS case 1: start_ip_address and end_ip_address is NOT equals to 0.0.0.0

resource "azurerm_sql_firewall_rule" "pass_1" {
  name                = "pud_AZ_SQL_FW"
  resource_group_name = azurerm_resource_group.pud_rg.name
  server_name         = azurerm_sql_server.pud_sql_server.name
  start_ip_address    = "10.0.0.0"
  end_ip_address      = "20.0.0.0"
}

# PASS case 2: start_ip_address is NOT equals to 0.0.0.0

resource "azurerm_sql_firewall_rule" "pass_2" {
  name                = "pud_AZ_SQL_FW"
  resource_group_name = azurerm_resource_group.pud_rg.name
  server_name         = azurerm_sql_server.pud_fail_server.name
  start_ip_address    = "10.0.0.0"
  end_ip_address      = "0.0.0.0"
}

resource "azurerm_mssql_firewall_rule" "pass_2" {
  name                = "pud_AZ_SQL_FW"
  start_ip_address    = "10.0.0.0"
  end_ip_address      = "0.0.0.0"
}

# FAIL case: start_ip_address and end_ip_address equals to 0.0.0.0


resource "azurerm_sql_firewall_rule" "fail" {
  name                = "pud_AZ_SQL_FW"
  resource_group_name = azurerm_resource_group.pud_rg.name
  server_name         = azurerm_sql_server.pud_fail_server.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
}

resource "azurerm_mssql_firewall_rule" "fail" {
  name                = "pud_AZ_SQL_FW"
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
}

