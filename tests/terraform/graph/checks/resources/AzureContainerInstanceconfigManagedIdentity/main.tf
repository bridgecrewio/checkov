# PASS case: "identity" block exists & "identity.type" is not empty

resource "azurerm_container_group" "pass" {
  name                = "pud_pass_container"
  resource_group_name = azurerm_resource_group.pudrg.name
  location            = azurerm_resource_group.pudrg.location
  ip_address_type     = "None"
  os_type             = "Linux"
  container {
    name   = "dep-containerinstance-3"
    image  = "mcr.microsoft.com/azuredocs/aci-helloworld:latest"
    cpu    = "0.5"
    memory = "1.5"
    ports {
      port = 443
    }
    secure_environment_variables={
      minLegth=5
      maxLength=10
      password=1234567
    }
  }
  container {
    name   = "dep-containerinstance-4"
    image  = "mcr.microsoft.com/azuredocs/aci-helloworld:latest"
    cpu    = "0.5"
    memory = "1.5"
  }
  identity {
    type         = "SystemAssigned"
    identity_ids = [
      azurerm_user_assigned_identity.dep-uai-j1-2-rlp-74782.id
    ]
  }
}


# FAIL case: "identity" block does not exist

resource "azurerm_container_group" "fail" {
  name                = "pud_fail_container"
  resource_group_name = azurerm_resource_group.pudrg.name
  location            = azurerm_resource_group.pudrg.location
  ip_address_type     = "None"
  os_type             = "Linux"
  container {
    name   = "dep-containerinstance-3"
    image  = "mcr.microsoft.com/azuredocs/aci-helloworld:latest"
    cpu    = "0.5"
    memory = "1.5"
    ports {
      port = 443
    }
    secure_environment_variables={
      minLegth=5
      maxLength=10
      password=1234567
    }
  }
  container {
    name   = "dep-containerinstance-4"
    image  = "mcr.microsoft.com/azuredocs/aci-helloworld:latest"
    cpu    = "0.5"
    memory = "1.5"
  }
}
