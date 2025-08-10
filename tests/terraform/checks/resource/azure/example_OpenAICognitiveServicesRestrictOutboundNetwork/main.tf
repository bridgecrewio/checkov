resource "azurerm_cognitive_account" "pass_openai" {
  name                = "openai-account"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "OpenAI"
  identity {
    type = "a"
  }
  sku_name = "S0"

  outbound_network_access_restricted = true
  fqdns = ["openai.example.com"]  # Valid FQDN should pass the check

  tags = {
    Acceptance = "Test"
  }
}

resource "azurerm_cognitive_account" "fail_openai_missing_fqdns" {
  name                = "openai-account-missing-fqdns"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "OpenAI"
  identity {
    type = "a"
  }
  sku_name = "S0"

  outbound_network_access_restricted = true
  fqdns = []  # Empty list of FQDNs should trigger failure

  tags = {
    Acceptance = "Test"
  }
}

resource "azurerm_cognitive_account" "fail_openai_missing_outbound_network_access" {
  name                = "openai-account-missing-outbound-network-access"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "OpenAI"
  identity {
    type = "a"
  }
  sku_name = "S0"

  # Missing outbound_network_access_restricted field should trigger failure
  fqdns = ["openai.example.com"]

  tags = {
    Acceptance = "Test"
  }
}

resource "azurerm_cognitive_account" "pass_non_openai" {
  name                = "non-openai-account"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "TextAnalytics"  # Non-OpenAI kind should automatically pass the check
  identity {
    type = "a"
  }
  sku_name = "S0"

  outbound_network_access_restricted = false
  fqdns = []  # Doesn't matter since kind is not OpenAI

  tags = {
    Acceptance = "Test"
  }
}

resource "azurerm_cognitive_account" "fail_openai_missing_fqdns_and_outbound_network_access" {
  name                = "openai-account-missing-both"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "OpenAI"
  identity {
    type = "a"
  }
  sku_name = "S0"

  # Missing outbound access should trigger failure
  # Empty FQDNs list should trigger failure

  tags = {
    Acceptance = "Test"
  }
}

resource "azurerm_cognitive_account" "pass_openai_multiple_fqdns" {
  name                = "openai-account-multiple-fqdns"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "OpenAI"
  identity {
    type = "a"
  }
  sku_name = "S0"

  outbound_network_access_restricted = true
  fqdns = ["openai1.example.com", "openai2.example.com", "openai3.example.com"]  # Multiple FQDNs should pass

  tags = {
    Acceptance = "Test"
  }
}

resource "azurerm_cognitive_account" "fail_openai_missing_fqdns_but_present_outbound_network_access" {
  name                = "openai-account-failed-missing-fqdns"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "OpenAI"
  identity {
    type = "a"
  }
  sku_name = "S0"

  outbound_network_access_restricted = true  # Present outbound access but missing FQDNs
  fqdns = []  # Empty list of FQDNs should trigger failure

  tags = {
    Acceptance = "Test"
  }
}

resource "azurerm_cognitive_account" "fail_openai_no_outbound_access_and_multiple_fqdns" {
  name                = "openai-account-failed-no-outbound-access-multiple-fqdns"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "OpenAI"
  identity {
    type = "a"
  }
  sku_name = "S0"

  # Missing outbound access but multiple FQDNs present
  fqdns = ["openai1.example.com", "openai2.example.com", "openai3.example.com"]  # Multiple FQDNs should trigger failure due to missing outbound access

  tags = {
    Acceptance = "Test"
  }
}
