resource "azurerm_security_center_subscription_pricing" "fail" {
  tier          = "Free"
  resource_type = "DNS"
}

resource "azurerm_security_center_subscription_pricing" "pass" {
  tier          = "Standard"
  xresource_type = "dns"
}

