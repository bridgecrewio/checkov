#PASS case:
resource "azurerm_postgresql_flexible_server_firewall_rule" "pass" {
  name             = "prx-policy-auto"
  server_id        = azurerm_postgresql_flexible_server.prxpolicyauto.id
  start_ip_address = "10.0.0.0"
  end_ip_address   = "10.0.0.8"
}

#FAIL case 1:
resource "azurerm_postgresql_flexible_server_firewall_rule" "fail_1" {
  name             = "frwl-1"
  server_id        = azurerm_postgresql_flexible_server.frwl-1.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

#FAIL case 2:
resource "azurerm_postgresql_flexible_server_firewall_rule" "fail_2" {
  name             = "frwl-2"
  server_id        = azurerm_postgresql_flexible_server.frwl-2.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "192.168.10.0"
}

#FAIL case 3: 
resource "azurerm_postgresql_flexible_server_firewall_rule" "fail_3" {
  name             = "frwl-3"
  server_id        = azurerm_postgresql_flexible_server.frwl-3.id
  start_ip_address = "10.0.0.0"
  end_ip_address   = "255.255.255.255"
}