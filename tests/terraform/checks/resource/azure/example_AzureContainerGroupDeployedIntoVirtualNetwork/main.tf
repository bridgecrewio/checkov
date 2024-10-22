
           resource "azurerm_container_group" "fail" {
              name                = "example-continst"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              ip_address_type     = "public"
              dns_name_label      = "aci-label"
              os_type             = "Linux"

              container {
                name   = "hello-world"
                image  = "microsoft/aci-helloworld:latest"
                cpu    = "0.5"
                memory = "1.5"

                ports {
                  port     = 443
                  protocol = "TCP"
                }
              }

              container {
                name   = "sidecar"
                image  = "microsoft/aci-tutorial-sidecar"
                cpu    = "0.5"
                memory = "1.5"
              }
            }

        resource "azurerm_container_group" "pass" {
              name                = "example-continst"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              ip_address_type     = "public"
              dns_name_label      = "aci-label"
              os_type             = "Linux"

              container {
                name   = "hello-world"
                image  = "microsoft/aci-helloworld:latest"
                cpu    = "0.5"
                memory = "1.5"

                ports {
                  port     = 443
                  protocol = "TCP"
                }
              }

              container {
                name   = "sidecar"
                image  = "microsoft/aci-tutorial-sidecar"
                cpu    = "0.5"
                memory = "1.5"
              }

              subnet_ids=[module.subnets["snet_aci"].id]
            }
