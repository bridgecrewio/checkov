
# Case 1: Pass: tier is Standard and resource_type is Arm

resource "azurerm_security_center_subscription_pricing" "pass_1" {
  tier          = "Standard"
  resource_type = "Arm"
}

# Case 2: Fails as "tier" should be "Standard"

resource "azurerm_security_center_subscription_pricing" "fail_1" {
  tier          = "Free"
  resource_type = "arm"
}

# Case 3: Pass as policy should only check if the resource_type is "Arm"

resource "azurerm_security_center_subscription_pricing" "pass_2" {
  tier          = "Free"
  resource_type = "Dns"
}

# Case 4: Pass as policy should only check if the resource_type is "Arm"

resource "azurerm_security_center_subscription_pricing" "pass_3" {
  tier          = "Free"
  resource_type = "VirtualMachine"
}