resource "azurerm_api_management" "pass" {
  name                       = var.api.name
  location                   = var.location
  resource_group_name        = var.rg_name
  publisher_name             = var.api.publisher_name
  publisher_email            = var.api.publisher_email
  sku_name                   = var.api.sku_name
  client_certificate_enabled = var.client_certificate
  virtual_network_type       = var.api.virtual_network_type

  virtual_network_configuration {
    subnet_id = var.api.subnet_id
  }
}

resource "azurerm_api_management" "fail" {
  name                       = var.api.name
  location                   = var.location
  resource_group_name        = var.rg_name
  publisher_name             = var.api.publisher_name
  publisher_email            = var.api.publisher_email
  sku_name                   = var.api.sku_name
  client_certificate_enabled = var.client_certificate
  virtual_network_type       = var.api.virtual_network_type

  security {
    enable_back_end_ssl30 = true
  }

  virtual_network_configuration {
    subnet_id = var.api.subnet_id
  }
}

resource "azurerm_api_management" "fail2" {
  name                       = var.api.name
  location                   = var.location
  resource_group_name        = var.rg_name
  publisher_name             = var.api.publisher_name
  publisher_email            = var.api.publisher_email
  sku_name                   = var.api.sku_name
  client_certificate_enabled = var.client_certificate
  virtual_network_type       = var.api.virtual_network_type

  security {
    enable_backend_tls10 = true
  }

  virtual_network_configuration {
    subnet_id = var.api.subnet_id
  }
}

resource "azurerm_api_management" "fail3" {
  name                       = var.api.name
  location                   = var.location
  resource_group_name        = var.rg_name
  publisher_name             = var.api.publisher_name
  publisher_email            = var.api.publisher_email
  sku_name                   = var.api.sku_name
  client_certificate_enabled = var.client_certificate
  virtual_network_type       = var.api.virtual_network_type

  security {
    enable_frontend_ssl30 = true
  }

  virtual_network_configuration {
    subnet_id = var.api.subnet_id
  }
}

resource "azurerm_api_management" "fail4" {
  name                       = var.api.name
  location                   = var.location
  resource_group_name        = var.rg_name
  publisher_name             = var.api.publisher_name
  publisher_email            = var.api.publisher_email
  sku_name                   = var.api.sku_name
  client_certificate_enabled = var.client_certificate
  virtual_network_type       = var.api.virtual_network_type

  security {
    enable_frontend_tls10 = true
  }

  virtual_network_configuration {
    subnet_id = var.api.subnet_id
  }
}
resource "azurerm_api_management" "fail5" {
  name                       = var.api.name
  location                   = var.location
  resource_group_name        = var.rg_name
  publisher_name             = var.api.publisher_name
  publisher_email            = var.api.publisher_email
  sku_name                   = var.api.sku_name
  client_certificate_enabled = var.client_certificate
  virtual_network_type       = var.api.virtual_network_type

  security {
    enable_frontend_tls11 = true
  }

  virtual_network_configuration {
    subnet_id = var.api.subnet_id
  }
}
