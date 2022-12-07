resource "azurerm_cosmosdb_account" "pass" {
  name                          = "pike-sql"
  location                      = "uksouth"
  resource_group_name           = "pike"
  offer_type                    = "Standard"
  kind                          = "GlobalDocumentDB"
  local_authentication_disabled = true
  enable_free_tier              = true

  consistency_policy {
    consistency_level       = "Session"
    max_interval_in_seconds = 5
    max_staleness_prefix    = 100
  }

  geo_location {
    location          = "uksouth"
    failover_priority = 0
  }
  tags = {
    "defaultExperience"       = "Core (SQL)"
    "hidden-cosmos-mmspecial" = ""
  }
}

resource "azurerm_cosmosdb_account" "fail" {
  name                          = "pike-sql"
  location                      = "uksouth"
  resource_group_name           = "pike"
  offer_type                    = "Standard"
  kind                          = "GlobalDocumentDB"
  local_authentication_disabled = false
  enable_free_tier              = true

  consistency_policy {
    consistency_level       = "Session"
    max_interval_in_seconds = 5
    max_staleness_prefix    = 100
  }

  geo_location {
    location          = "uksouth"
    failover_priority = 0
  }
  tags = {
    "defaultExperience"       = "Core (SQL)"
    "hidden-cosmos-mmspecial" = ""
  }
}

resource "azurerm_cosmosdb_account" "fail2" {
  name                = "pike-sql"
  location            = "uksouth"
  resource_group_name = "pike"
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  //local_authentication_disabled = false
  enable_free_tier = true

  consistency_policy {
    consistency_level       = "Session"
    max_interval_in_seconds = 5
    max_staleness_prefix    = 100
  }

  geo_location {
    location          = "uksouth"
    failover_priority = 0
  }
  tags = {
    "defaultExperience"       = "Core (SQL)"
    "hidden-cosmos-mmspecial" = ""
  }
}

## SHOULD ignore: local_authentication_disabled can only be set on SQL api - kind = "GlobalDocumentDB"
resource "azurerm_cosmosdb_account" "ignore" {
  name                          = "cosmos-db"
  location                      = azurerm_resource_group.rg.location
  resource_group_name           = azurerm_resource_group.rg.name
  offer_type                    = "Standard"
  kind                          = "MongoDB"
  local_authentication_disabled = true

  consistency_policy {
    consistency_level       = "BoundedStaleness"
    max_interval_in_seconds = 300
    max_staleness_prefix    = 100000
  }

  geo_location {
    location          = azurerm_resource_group.rg.location
    failover_priority = 0
  }
}


resource "azurerm_cosmosdb_account" "ignore2" {
  name                          = "cosmos-db"
  location                      = azurerm_resource_group.rg.location
  resource_group_name           = azurerm_resource_group.rg.name
  offer_type                    = "Standard"
  kind                          = "MongoDB"
  local_authentication_disabled = false

  consistency_policy {
    consistency_level       = "BoundedStaleness"
    max_interval_in_seconds = 300
    max_staleness_prefix    = 100000
  }

  geo_location {
    location          = azurerm_resource_group.rg.location
    failover_priority = 0
  }
}


resource "azurerm_cosmosdb_account" "ignore3" {
  name                = "cosmos-db"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  offer_type          = "Standard"
  kind                = "MongoDB"

  consistency_policy {
    consistency_level       = "BoundedStaleness"
    max_interval_in_seconds = 300
    max_staleness_prefix    = 100000
  }

  geo_location {
    location          = azurerm_resource_group.rg.location
    failover_priority = 0
  }
}