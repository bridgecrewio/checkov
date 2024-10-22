
resource "azurerm_api_management" "fail" {
  name                = "example-apim"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  publisher_name      = "My Company"
  publisher_email     = "company@terraform.io"

  sku_name = "Consumption"

  policy {
    xml_content = <<XML
                    <policies>
                      <inbound />
                      <backend />
                      <outbound />
                      <on-error />
                    </policies>
                XML

  }
  security {
    enable_frontend_tls10 = false
    enable_frontend_tls11 = false
    enable_frontend_ssl30 = false
  }

  public_network_access_enabled = true
}


resource "azurerm_api_management" "fail2" {
  name                = "example-apim"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  publisher_name      = "My Company"
  publisher_email     = "company@terraform.io"

  sku_name = "Consumption"
  client_certificate_enabled = false

  policy {
    xml_content = <<XML
                    <policies>
                      <inbound />
                      <backend />
                      <outbound />
                      <on-error />
                    </policies>
                XML

  }
  security {
    enable_frontend_tls10 = false
    enable_frontend_tls11 = false
    enable_frontend_ssl30 = false
  }

  identity {

  }
}


resource "azurerm_api_management" "pass" {
  name                = "example-apim"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  publisher_name      = "My Company"
  publisher_email     = "company@terraform.io"

  sku_name = "Consumption"
  client_certificate_enabled = true

  policy {
    xml_content = <<XML
                    <policies>
                      <inbound />
                      <backend />
                      <outbound />
                      <on-error />
                    </policies>
                XML

  }
  security {
    enable_frontend_tls10 = false
    enable_frontend_tls11 = false
    enable_frontend_ssl30 = false
  }

 public_network_access_enabled = false
}