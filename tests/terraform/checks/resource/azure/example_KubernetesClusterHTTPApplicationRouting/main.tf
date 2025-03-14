resource "azurerm_kubernetes_cluster" "fail" {
  http_application_routing_enabled = true
}

resource "azurerm_kubernetes_cluster" "pass_false" {
  http_application_routing_enabled = false
}

resource "azurerm_kubernetes_cluster" "pass_missing" {
  name = "example-aks1"
}
