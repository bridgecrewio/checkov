resource "azurerm_cdn_endpoint" "pass" {
  name                      = var.cdn.name
  profile_name              = var.cdn.profile_name
  location                  = var.cdn.location
  resource_group_name       = var.rg_name
  is_http_allowed           = false
  is_https_allowed          = true
  origin_host_header        = var.cdn.origin_host_header
  origin_path               = var.cdn.origin_path
  content_types_to_compress = var.content_types_to_compress

  dynamic "origin" {
    for_each = var.origins
    content {
      name      = origin.value["name"]
      host_name = origin.value["host_name"]
    }
  }
}

resource "azurerm_cdn_endpoint" "fail" {
  name                      = var.cdn.name
  profile_name              = var.cdn.profile_name
  location                  = var.cdn.location
  resource_group_name       = var.rg_name
  is_http_allowed           = true
  is_https_allowed          = false
  origin_host_header        = var.cdn.origin_host_header
  origin_path               = var.cdn.origin_path
  content_types_to_compress = var.content_types_to_compress

  dynamic "origin" {
    for_each = var.origins
    content {
      name      = origin.value["name"]
      host_name = origin.value["host_name"]
    }
  }
}

resource "azurerm_cdn_endpoint" "pass2" {
  name                      = var.cdn.name
  profile_name              = var.cdn.profile_name
  location                  = var.cdn.location
  resource_group_name       = var.rg_name
  origin_host_header        = var.cdn.origin_host_header
  origin_path               = var.cdn.origin_path
  content_types_to_compress = var.content_types_to_compress

  dynamic "origin" {
    for_each = var.origins
    content {
      name      = origin.value["name"]
      host_name = origin.value["host_name"]
    }
  }
}