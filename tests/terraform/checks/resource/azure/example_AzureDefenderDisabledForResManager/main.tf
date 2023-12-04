
# Case 1: Pass: tier is Standard and resource_type is Arm

resource "azurerm_security_center_subscription_pricing" "pass" {
  tier          = "Standard"
  resource_type = "Arm"
}

# Case 2: Fails as "tier" should be "Standard"

resource "azurerm_security_center_subscription_pricing" "fail_1" {
  tier          = "Free"
  resource_type = "arm"
}

# Case 3: Fails as "resource_type" should be "Arm"

resource "azurerm_security_center_subscription_pricing" "fail_2" {
  tier          = "Standard"
  resource_type = "Dns"
}

