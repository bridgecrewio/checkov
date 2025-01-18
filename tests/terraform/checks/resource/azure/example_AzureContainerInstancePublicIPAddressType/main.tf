# Fail: public IP address type
resource "azurerm_container_group" "fail_public" {
  name                = "example-continst"
  ip_address_type     = "Public"
}

# Fail: IP address type not set
resource "azurerm_container_group" "fail_notset" {
  name                = "example-continst"
}

# Pass: IP address type not public
resource "azurerm_container_group" "pass" {
  name                = "example-continst"
  ip_address_type     = "Private"
}