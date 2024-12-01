# Fail: SKU is not Basic and tls is disabled
resource "azurerm_spring_cloud_service" "fail" {
  name                = "example-springcloud"
  resource_group_name = azurerm_resource_group.fail.name
  location            = azurerm_resource_group.fail.location
  sku_tier            = "Standard" # Computed, so unknown if not set
}

resource "azurerm_spring_cloud_app" "fail" {
  name                = "example-springcloudapp"
  resource_group_name = azurerm_resource_group.fail.name
  service_name        = azurerm_spring_cloud_service.fail.name
  tls_enabled         = false # defaults to false

  identity {
    type = "SystemAssigned"
  }
}

# Pass: SKU is Basic and tls is disabled
resource "azurerm_spring_cloud_service" "pass_basic" {
  name                = "example-springcloud"
  resource_group_name = azurerm_resource_group.pass_basic.name
  location            = azurerm_resource_group.pass_basic.location
  sku_tier            = "Basic" # Computed, so unknown if not set
}

resource "azurerm_spring_cloud_app" "pass_basic" {
  name                = "example-springcloudapp"
  resource_group_name = azurerm_resource_group.pass_basic.name
  service_name        = azurerm_spring_cloud_service.pass_basic.name
  tls_enabled         = false # defaults to false

  identity {
    type = "SystemAssigned"
  }
}

# Pass: SKU is not set and tls is disabled
resource "azurerm_spring_cloud_service" "pass_notset" {
  name                = "example-springcloud"
  resource_group_name = azurerm_resource_group.pass_notset.name
  location            = azurerm_resource_group.pass_notset.location
  sku_tier            = "Basic" # Computed, so unknown if not set
}

resource "azurerm_spring_cloud_app" "unknown_notset" {
  name                = "example-springcloudapp"
  resource_group_name = azurerm_resource_group.pass_notset.name
  service_name        = azurerm_spring_cloud_service.pass_notset.name
  tls_enabled         = false # defaults to false

  identity {
    type = "SystemAssigned"
  }
}

# Fail: SKU is not Basic and tls is not set
resource "azurerm_spring_cloud_service" "fail_notset" {
  name                = "example-springcloud"
  resource_group_name = azurerm_resource_group.fail_notset.name
  location            = azurerm_resource_group.fail_notset.location
  sku_tier            = "Standard" # Computed, so unknown if not set
}

resource "azurerm_spring_cloud_app" "fail_notset" {
  name                = "example-springcloudapp"
  resource_group_name = azurerm_resource_group.fail_notset.name
  service_name        = azurerm_spring_cloud_service.fail_notset.name
  # not setting tls_enabled defaults to false

  identity {
    type = "SystemAssigned"
  }
}

# Pass: SKU is not Basic and tls is true
resource "azurerm_spring_cloud_service" "pass" {
  name                = "example-springcloud"
  resource_group_name = azurerm_resource_group.pass.name
  location            = azurerm_resource_group.pass.location
  sku_tier            = "Standard" # Computed, so unknown if not set
}

resource "azurerm_spring_cloud_app" "pass" {
  name                = "example-springcloudapp"
  resource_group_name = azurerm_resource_group.pass.name
  service_name        = azurerm_spring_cloud_service.pass.name
  tls_enabled         = true # defaults to false

  identity {
    type = "SystemAssigned"
  }
}

