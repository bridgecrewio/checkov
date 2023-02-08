resource "azurerm_cdn_endpoint_custom_domain" "pass" {
  name            = "example-domain"
  cdn_endpoint_id = azurerm_cdn_endpoint.example.id
  host_name       = "${azurerm_dns_cname_record.example.name}.${data.azurerm_dns_zone.example.name}"
}

resource "azurerm_cdn_endpoint_custom_domain" "pass2" {
  name            = "example-domain"
  cdn_endpoint_id = azurerm_cdn_endpoint.example.id
  host_name       = "${azurerm_dns_cname_record.example.name}.${data.azurerm_dns_zone.example.name}"
  cdn_managed_https {
    certificate_type = "dedicated"
    protocol_type    = "IPBased"
    tls_version      = "TLS12"
  }
}

resource "azurerm_cdn_endpoint_custom_domain" "pass3" {
  name            = "example-domain"
  cdn_endpoint_id = azurerm_cdn_endpoint.example.id
  host_name       = "${azurerm_dns_cname_record.example.name}.${data.azurerm_dns_zone.example.name}"
  user_managed_https {
    tls_version              = "TLS12"
    key_vault_certificate_id = ""
  }
}

resource "azurerm_cdn_endpoint_custom_domain" "fail" {
  name            = "example-domain"
  cdn_endpoint_id = azurerm_cdn_endpoint.example.id
  host_name       = "${azurerm_dns_cname_record.example.name}.${data.azurerm_dns_zone.example.name}"
  user_managed_https {
    tls_version              = "TLS10"
    key_vault_certificate_id = ""
  }
}

resource "azurerm_cdn_endpoint_custom_domain" "fail2" {
  name            = "example-domain"
  cdn_endpoint_id = azurerm_cdn_endpoint.example.id
  host_name       = "${azurerm_dns_cname_record.example.name}.${data.azurerm_dns_zone.example.name}"
  cdn_managed_https {
    certificate_type = "dedicated"
    tls_version      = "None"
    protocol_type    = "IPBased"
  }
}